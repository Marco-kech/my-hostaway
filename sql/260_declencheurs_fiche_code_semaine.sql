-- 260 — Trois déclencheurs Hostaway de plus : fiche d'arrivée disponible, code de porte créé, jour de la semaine.
-- Nouvelles variables dans les brouillons : {lien_fiche} {lien_sejour} {code_serrure}.
-- Toujours des brouillons, jamais d'envoi. Ajout pur.

alter table modele_message add column if not exists jours_semaine text[];
alter table modele_message add column if not exists heure_envoi time;
alter table modele_message add column if not exists jour_arrivee_inclus boolean not null default true;
alter table modele_message add column if not exists jour_depart_inclus boolean not null default true;

create or replace function auto_message_composer(p_corps text, p_resa uuid) returns text
language plpgsql stable security definer set search_path = public as $f$
declare r record; t text := coalesce(p_corps, ''); nuits int; k text; v text; vals jsonb; base text; jeton text;
begin
  select re.tenant_id, re.arrivee, re.depart, re.prix_total, re.montant_paye, re.canal::text as canal, re.nb_personnes,
         re.reference_canal, re.acces_voyageur, to_jsonb(re) -> 'donnees_source' ->> 'lockCode' as code_serrure,
         b.nom as bien, b.adresse, coalesce(b.parametres, '{}'::jsonb) as p,
         vo.nom as voyageur, vo.email, vo.tel
    into r
    from reservation re left join bien b on b.id = re.bien_id left join voyageur vo on vo.id = re.voyageur_id
   where re.id = p_resa;
  if not found then return t; end if;
  nuits := greatest(1, coalesce(r.depart - r.arrivee, 1));
  select coalesce((select g.url_base from parcours_reglage g where g.tenant_id = r.tenant_id), 'https://marco-kech.github.io/my-hostaway/') into base;
  select c.token into jeton from checkin_online c where c.reservation_id = p_resa and coalesce(c.statut, '') <> 'rempli' limit 1;
  vals := jsonb_build_object(
    'nom', coalesce(r.voyageur, ''), 'prenom', split_part(coalesce(r.voyageur, ''), ' ', 1),
    'email', coalesce(r.email, ''), 'tel', coalesce(r.tel, ''),
    'bien', coalesce(r.bien, ''), 'adresse', coalesce(r.adresse, ''), 'ville', coalesce(r.p->>'ville', ''),
    'arrivee', coalesce(to_char(r.arrivee, 'DD/MM/YYYY'), ''), 'depart', coalesce(to_char(r.depart, 'DD/MM/YYYY'), ''),
    'nuits', nuits::text, 'canal', coalesce(r.canal, ''), 'nb_personnes', coalesce(r.nb_personnes::text, ''),
    'prix_total', replace(to_char(coalesce(r.prix_total, 0), 'FM999G999G990'), ',', ' ') || ' MAD',
    'montant_paye', replace(to_char(coalesce(r.montant_paye, 0), 'FM999G999G990'), ',', ' ') || ' MAD',
    'reste_du', replace(to_char(greatest(coalesce(r.prix_total, 0) - coalesce(r.montant_paye, 0), 0), 'FM999G999G990'), ',', ' ') || ' MAD',
    'heure_arrivee', coalesce(r.p->>'heure_arrivee', '15:00'), 'heure_depart', coalesce(r.p->>'heure_depart', '11:00'),
    'code_porte', coalesce(r.p->>'code_porte', ''), 'wifi_nom', coalesce(r.p->>'wifi_nom', ''), 'wifi_mdp', coalesce(r.p->>'wifi_mdp', ''),
    'instructions_arrivee', coalesce(r.p->>'instructions_arrivee', ''), 'contact_urgence', coalesce(r.p->>'contact_urgence', ''),
    'reglement', coalesce(r.p->>'reglement_interieur', ''), 'ref_canal', coalesce(r.reference_canal, ''),
    'date_aujourdhui', to_char(now() at time zone 'Africa/Casablanca', 'DD/MM/YYYY'));
  vals := vals || jsonb_build_object(
    'code_serrure', coalesce(r.code_serrure, ''),
    'lien_fiche', case when jeton is null then '' else base || '#checkin=' || jeton end,
    'lien_sejour', case when r.acces_voyageur is null then '' else base || 'sejour/#/sejour/' || r.acces_voyageur end,
    'lien_avis', case when r.acces_voyageur is null then '' else base || 'avis.html#' || r.acces_voyageur end);
  for k, v in select * from jsonb_each_text(vals) loop
    t := replace(t, '{' || k || '}', v);
  end loop;
  return t;
end $f$;

create or replace function auto_message_fiche_dispo() returns trigger
language plpgsql security definer set search_path = public as $f$
begin
  begin
    if new.reservation_id is not null and coalesce(new.statut, '') <> 'rempli' then
      perform auto_message_preparer(new.tenant_id, new.reservation_id, 'fiche_disponible', new.id);
    end if;
  exception when others then
    raise warning 'auto_message_fiche_dispo : %', sqlerrm;
  end;
  return null;
end $f$;

drop trigger if exists zz_auto_message_fiche_dispo on checkin_online;
create trigger zz_auto_message_fiche_dispo after insert on checkin_online
  for each row execute function auto_message_fiche_dispo();

-- Code de porte : celui que la plateforme transmet avec la réservation. Un nouveau code (dates modifiées) redonne un brouillon.
create or replace function auto_message_code() returns trigger
language plpgsql security definer set search_path = public as $f$
declare nouveau text; ancien text;
begin
  begin
    nouveau := nullif(trim(to_jsonb(new) -> 'donnees_source' ->> 'lockCode'), '');
    if tg_op = 'UPDATE' then ancien := nullif(trim(to_jsonb(old) -> 'donnees_source' ->> 'lockCode'), ''); end if;
    if nouveau is not null and nouveau is distinct from ancien
       and new.statut::text = 'confirmee' and new.depart >= current_date then
      perform auto_message_preparer(new.tenant_id, new.id, 'code_porte', md5(new.id::text || nouveau)::uuid);
    end if;
  exception when others then
    raise warning 'auto_message_code : %', sqlerrm;
  end;
  return null;
end $f$;

drop trigger if exists zz_auto_message_code on reservation;
create trigger zz_auto_message_code after insert or update on reservation
  for each row execute function auto_message_code();

-- Jour de la semaine : pour les voyageurs en séjour, les jours cochés, à partir de l'heure choisie (9 h par défaut).
create or replace function auto_message_semaine() returns int
language plpgsql security definer set search_path = public as $f$
declare c record; j uuid; mid uuid; n int := 0;
begin
  for c in
    with loc as (
      select mo.id as modele_id, mo.tenant_id, mo.canal, mo.corps, mo.jours_semaine, mo.heure_envoi,
             mo.jour_arrivee_inclus, mo.jour_depart_inclus,
             (now() at time zone coalesce(g.fuseau, 'Africa/Casablanca')) as ici
        from modele_message mo left join parcours_reglage g on g.tenant_id = mo.tenant_id
       where mo.actif and mo.evenement = 'jour_semaine' and mo.jours_semaine is not null
    )
    select l.modele_id, l.tenant_id, l.canal, l.corps, r.id as resa, r.voyageur_id,
           md5(r.id::text || (l.ici::date)::text)::uuid as source
      from loc l join reservation r on r.tenant_id = l.tenant_id
     where r.statut::text = 'confirmee' and l.ici::date between r.arrivee and r.depart
       and (l.ici::date <> r.arrivee or l.jour_arrivee_inclus) and (l.ici::date <> r.depart or l.jour_depart_inclus)
       and (array['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'])[extract(dow from l.ici)::int + 1] = any(l.jours_semaine)
       and l.ici::time >= coalesce(l.heure_envoi, '09:00'::time)
       and not exists (select 1 from auto_message_journal a where a.modele_id = l.modele_id and a.evenement = 'jour_semaine'
                        and a.source_id = md5(r.id::text || (l.ici::date)::text)::uuid)
     limit 300
  loop
    begin
      j := null;
      insert into auto_message_journal (tenant_id, reservation_id, modele_id, evenement, source_id)
        values (c.tenant_id, c.resa, c.modele_id, 'jour_semaine', c.source)
        on conflict (modele_id, evenement, source_id) do nothing returning id into j;
      if j is null then continue; end if;
      insert into message (tenant_id, reservation_id, voyageur_id, canal, sens, corps, statut)
        values (c.tenant_id, c.resa, c.voyageur_id, c.canal, 'sortant', auto_message_composer(c.corps, c.resa), 'brouillon')
        returning id into mid;
      update auto_message_journal set message_id = mid where id = j;
      n := n + 1;
    exception when others then
      raise warning 'auto_message_semaine : %', sqlerrm;
    end;
  end loop;
  return n;
end $f$;

revoke all on function auto_message_composer(text, uuid) from public, anon, authenticated;
revoke all on function auto_message_semaine() from public, anon, authenticated;

do $c$
begin
  if exists (select 1 from cron.job where jobname = 'auto-message-echeances') then
    perform cron.unschedule('auto-message-echeances');
  end if;
  perform cron.schedule('auto-message-echeances', '*/15 * * * *',
    'select public.auto_message_echeances(), public.auto_message_dates(), public.auto_message_semaine()');
end $c$;
