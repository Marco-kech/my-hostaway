-- 180 — Parcours du voyageur (1/2) : liens automatiques et fiche voyageur complète.
-- Ajout pur : aucune colonne ni règle existante n'est retirée.

-- 1) La fiche voyageur reçoit les accompagnants, la date de naissance, le pays et l'accord WhatsApp.
alter table checkin_online
  add column if not exists date_naissance date,
  add column if not exists pays text,
  add column if not exists voyageurs jsonb not null default '[]'::jsonb,
  add column if not exists accord_whatsapp boolean not null default false;

create or replace function parcours_date(p text) returns date
language plpgsql immutable as $f$
begin
  if p is null or p !~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' then return null; end if;
  return p::date;
exception when others then return null;
end $f$;

-- 2) Les deux liens se créent seuls dès qu'une réservation est confirmée.
--    Une réservation annulée perd son lien d'application.
create or replace function parcours_lien_avant() returns trigger
language plpgsql as $f$
begin
  if new.statut::text = 'confirmee' and new.acces_voyageur is null then
    new.acces_voyageur := replace(gen_random_uuid()::text, '-', '');
  elsif new.statut::text = 'annulee' and new.acces_voyageur is not null then
    new.acces_voyageur := null;
  end if;
  return new;
end $f$;

create or replace function parcours_fiche_apres() returns trigger
language plpgsql security definer set search_path = public as $f$
begin
  if new.statut::text = 'confirmee'
     and not exists (select 1 from checkin_online c where c.reservation_id = new.id) then
    insert into checkin_online (tenant_id, reservation_id) values (new.tenant_id, new.id);
  end if;
  return null;
end $f$;

drop trigger if exists parcours_lien_avant on reservation;
create trigger parcours_lien_avant before insert or update of statut on reservation
  for each row execute function parcours_lien_avant();
drop trigger if exists parcours_fiche_apres on reservation;
create trigger parcours_fiche_apres after insert or update of statut on reservation
  for each row execute function parcours_fiche_apres();

-- 3) Ce que la page de la fiche a le droit de savoir, par son lien uniquement.
create or replace function checkin_infos(p_token text) returns jsonb
language sql stable security definer set search_path = public as $f$
  select jsonb_build_object('statut', c.statut::text, 'bien', b.nom,
                            'arrivee', r.arrivee, 'depart', r.depart, 'nb', r.nb_personnes)
  from checkin_online c
  left join reservation r on r.id = c.reservation_id
  left join bien b on b.id = r.bien_id
  where p_token is not null and length(p_token) >= 16 and c.token = p_token limit 1;
$f$;

-- 4) Enregistrement de la fiche : mêmes contrôles qu'avant, plus les nouveaux champs.
--    Le téléphone et l'e-mail vont aussi sur la fiche du voyageur de la réservation,
--    sans jamais écraser une valeur déjà présente ; le WhatsApp seulement avec l'accord.
create or replace function checkin_remplir(p_token text, p_infos jsonb) returns text
language plpgsql security definer set search_path = public as $f$
declare v_id uuid; v_statut text; v_resa uuid; v_voy uuid; v_tel text; v_email text; v_accord boolean; v_liste jsonb;
begin
  if p_token is null or length(p_token) < 16 then return 'invalide'; end if;
  select c.id, c.statut::text, c.reservation_id into v_id, v_statut, v_resa from checkin_online c where c.token = p_token limit 1;
  if v_id is null then return 'invalide'; end if;
  if v_statut = 'rempli' then return 'deja_rempli'; end if;
  if nullif(trim(p_infos->>'nom'), '') is null or nullif(trim(p_infos->>'prenom'), '') is null then
    raise exception 'Nom et prénom sont obligatoires';
  end if;
  v_tel := left(nullif(trim(p_infos->>'telephone'), ''), 60);
  v_email := left(nullif(trim(p_infos->>'email'), ''), 200);
  v_accord := coalesce(p_infos->>'accord_whatsapp', '') in ('true', 't', '1') and v_tel is not null;
  select coalesce(jsonb_agg(jsonb_build_object(
           'nom', left(trim(e->>'nom'), 200), 'prenom', left(trim(coalesce(e->>'prenom', '')), 200),
           'date_naissance', parcours_date(e->>'date_naissance'),
           'nationalite', left(nullif(trim(e->>'nationalite'), ''), 100),
           'num_piece', left(nullif(trim(e->>'num_piece'), ''), 100))), '[]'::jsonb)
    into v_liste
    from (select e from jsonb_array_elements(
            case when jsonb_typeof(p_infos->'voyageurs') = 'array' then p_infos->'voyageurs' else '[]'::jsonb end) e
          limit 30) s
   where nullif(trim(e->>'nom'), '') is not null;
  update checkin_online set
    nom = left(trim(p_infos->>'nom'), 200), prenom = left(trim(p_infos->>'prenom'), 200),
    email = v_email, telephone = v_tel,
    nationalite = left(nullif(trim(p_infos->>'nationalite'), ''), 100),
    num_passeport = left(nullif(trim(p_infos->>'num_passeport'), ''), 100),
    date_naissance = parcours_date(p_infos->>'date_naissance'),
    pays = left(nullif(trim(p_infos->>'pays'), ''), 100),
    heure_arrivee = left(nullif(trim(p_infos->>'heure_arrivee'), ''), 20),
    nb_personnes = case when (p_infos->>'nb_personnes') ~ '^[0-9]{1,3}$' then (p_infos->>'nb_personnes')::int end,
    vehicule = left(nullif(trim(p_infos->>'vehicule'), ''), 200),
    plaque = left(nullif(trim(p_infos->>'plaque'), ''), 60),
    demandes_speciales = left(nullif(trim(p_infos->>'demandes_speciales'), ''), 2000),
    voyageurs = v_liste, accord_whatsapp = v_accord,
    statut = 'rempli', rempli_le = now()
  where id = v_id;
  select r.voyageur_id into v_voy from reservation r where r.id = v_resa;
  if v_voy is not null then
    update voyageur v set
      tel = coalesce(nullif(trim(v.tel), ''), v_tel),
      email = coalesce(nullif(trim(v.email), ''), v_email),
      whatsapp = case when v_accord then v_tel else v.whatsapp end
    where v.id = v_voy;
  end if;
  return 'ok';
end $f$;

revoke all on function checkin_infos(text) from public;
revoke all on function checkin_remplir(text, jsonb) from public;
grant execute on function checkin_infos(text) to anon, authenticated;
grant execute on function checkin_remplir(text, jsonb) to anon, authenticated;
revoke all on function parcours_date(text) from public;
grant execute on function parcours_date(text) to anon, authenticated, service_role;

-- 5) Rattrapage : les réservations déjà confirmées et pas encore terminées reçoivent leurs deux liens.
update reservation set acces_voyageur = replace(gen_random_uuid()::text, '-', '')
 where statut::text = 'confirmee' and acces_voyageur is null and depart >= current_date;
insert into checkin_online (tenant_id, reservation_id)
select r.tenant_id, r.id from reservation r
 where r.statut::text = 'confirmee' and r.depart >= current_date
   and not exists (select 1 from checkin_online c where c.reservation_id = r.id);
