-- 190 — Parcours du voyageur (2/2) : envoi automatique des trois messages.
-- Éteint par défaut : rien ne part tant que parcours_reglage.actif n'est pas mis à vrai.
-- Ajout pur : aucune table ni règle existante n'est modifiée.

create table if not exists parcours_reglage (
  tenant_id uuid primary key references tenant(id) on delete cascade,
  actif boolean not null default false,
  whatsapp_actif boolean not null default false,
  url_base text not null default 'https://marco-kech.github.io/my-hostaway/',
  pont_url text,
  fuseau text not null default 'Africa/Casablanca',
  heure_debut int not null default 9 check (heure_debut between 0 and 23),
  heure_fin int not null default 20 check (heure_fin between 1 and 24),
  jours_guide int not null default 15 check (jours_guide between 1 and 120),
  jours_rappel int not null default 3 check (jours_rappel between 0 and 30),
  lien_bienvenue_airbnb boolean not null default false,
  textes jsonb not null default '{}'::jsonb,
  maj timestamptz not null default now()
);

create table if not exists parcours_envoi (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenant(id) on delete cascade,
  reservation_id uuid not null references reservation(id) on delete cascade,
  etape text not null check (etape in ('bienvenue', 'guide', 'rappel')),
  canal text not null,
  statut text not null default 'envoye' check (statut in ('envoye', 'erreur', 'saute')),
  detail text,
  requete_id bigint,
  verifie boolean not null default false,
  message_id uuid,
  cree_le timestamptz not null default now(),
  unique (reservation_id, etape)
);
create index if not exists idx_parcours_envoi_tenant on parcours_envoi (tenant_id, cree_le desc);

alter table parcours_reglage enable row level security;
alter table parcours_envoi enable row level security;
drop policy if exists parcours_reglage_lecture on parcours_reglage;
create policy parcours_reglage_lecture on parcours_reglage for select to authenticated using (app_is_member(tenant_id));
drop policy if exists parcours_reglage_admin on parcours_reglage;
create policy parcours_reglage_admin on parcours_reglage for all to authenticated
  using (app_has_role(tenant_id, array['proprietaire_compte', 'administrateur']::role_membre[]))
  with check (app_has_role(tenant_id, array['proprietaire_compte', 'administrateur']::role_membre[]));
drop policy if exists parcours_envoi_lecture on parcours_envoi;
create policy parcours_envoi_lecture on parcours_envoi for select to authenticated using (app_is_member(tenant_id));
drop policy if exists parcours_envoi_reessai on parcours_envoi;
create policy parcours_envoi_reessai on parcours_envoi for delete to authenticated
  using (statut = 'erreur' and app_has_role(tenant_id, array['proprietaire_compte', 'administrateur']::role_membre[]));

-- Textes par défaut (modifiables dans parcours_reglage.textes). Balises : {prenom} {bien} {arrivee} {depart}
-- {lien_fiche} {lien_app}. Une ligne dont la balise de lien est vide est retirée du message.
create or replace function parcours_textes_defaut() returns jsonb language sql immutable as $f$
  select jsonb_build_object(
    'bienvenue', jsonb_build_object(
      'fr', E'Bonjour {prenom},\n\nMerci pour votre réservation à {bien}, du {arrivee} au {depart}. Nous sommes ravis de vous accueillir.\n\nPour préparer votre arrivée, merci de remplir la fiche d''enregistrement des voyageurs (2 minutes) : {lien_fiche}\n\nNous restons à votre disposition pour toute question.\n\nL''équipe DPM Conciergerie',
      'en', E'Hello {prenom},\n\nThank you for booking {bien}, from {arrivee} to {depart}. We look forward to welcoming you.\n\nTo prepare your arrival, please fill in the guest registration form (2 minutes): {lien_fiche}\n\nWe remain at your disposal for any question.\n\nThe DPM Conciergerie team'),
    'guide', jsonb_build_object(
      'fr', E'Bonjour {prenom},\n\nVotre séjour à {bien} approche. Voici votre guide du séjour, avec les informations pratiques du logement et les services que vous pouvez commander : {lien_app}\n\nSi ce n''est pas encore fait, merci de remplir la fiche d''enregistrement des voyageurs : {lien_fiche}\n\nÀ très bientôt,\nL''équipe DPM Conciergerie',
      'en', E'Hello {prenom},\n\nYour stay at {bien} is coming up. Here is your stay guide, with practical information about the home and the services you can order: {lien_app}\n\nIf not done yet, please fill in the guest registration form: {lien_fiche}\n\nSee you soon,\nThe DPM Conciergerie team'),
    'rappel', jsonb_build_object(
      'fr', E'Bonjour {prenom},\n\nVous arrivez bientôt à {bien} : arrivée le {arrivee}. Votre guide du séjour : {lien_app}\n\nIl reste à remplir la fiche d''enregistrement des voyageurs : {lien_fiche}\n\nBon voyage,\nL''équipe DPM Conciergerie',
      'en', E'Hello {prenom},\n\nYou will soon arrive at {bien}: check-in on {arrivee}. Your stay guide: {lien_app}\n\nThe guest registration form is still to be filled in: {lien_fiche}\n\nHave a good trip,\nThe DPM Conciergerie team'));
$f$;

create or replace function parcours_composer(p_modele text, p_valeurs jsonb) returns text
language plpgsql immutable as $f$
declare v_ligne text; v_out text := ''; v_cle text; v_garde boolean;
begin
  foreach v_ligne in array string_to_array(coalesce(p_modele, ''), E'\n') loop
    v_garde := true;
    foreach v_cle in array array['lien_fiche', 'lien_app'] loop
      if position('{' || v_cle || '}' in v_ligne) > 0 and coalesce(p_valeurs->>v_cle, '') = '' then v_garde := false; end if;
    end loop;
    if v_garde then
      for v_cle in select jsonb_object_keys(p_valeurs) loop
        v_ligne := replace(v_ligne, '{' || v_cle || '}', coalesce(p_valeurs->>v_cle, ''));
      end loop;
      v_out := v_out || v_ligne || E'\n';
    end if;
  end loop;
  return trim(both E'\n' from regexp_replace(v_out, E'\n{3,}', E'\n\n', 'g'));
end $f$;

-- Ce qui est dû maintenant pour une société, sans rien envoyer.
create or replace function parcours_plan_interne(p_tenant uuid, p_maintenant timestamptz)
returns table (reservation_id uuid, voyageur text, bien text, arrivee date, etape text, canal text, texte text, note text)
language plpgsql stable security definer set search_path = public as $f$
declare g parcours_reglage; r record; v_jour date; v_jours int; v_etape text; v_canal text; v_langue text; v_textes jsonb;
  v_val jsonb; v_fiche text; v_app text; v_txt text; v_note text; v_deja text[]; v_dernier timestamptz; v_fmt text := 'DD/MM/YYYY';
begin
  select * into g from parcours_reglage where tenant_id = p_tenant;
  if not found then return; end if;
  v_jour := (p_maintenant at time zone g.fuseau)::date;
  v_textes := parcours_textes_defaut() || coalesce(g.textes, '{}'::jsonb);
  for r in
    select x.id, x.arrivee, x.depart, x.canal::text as canal, x.source_id, x.acces_voyageur,
           v.nom as vnom, v.langue, v.whatsapp, b.nom as bnom, c.token as ctoken, c.statut::text as cstatut
      from reservation x
      left join voyageur v on v.id = x.voyageur_id
      left join bien b on b.id = x.bien_id
      left join checkin_online c on c.reservation_id = x.id
     where x.tenant_id = p_tenant and x.statut::text = 'confirmee' and x.arrivee >= v_jour
     order by x.arrivee
  loop
    select array_agg(e.etape), max(e.cree_le) into v_deja, v_dernier from parcours_envoi e where e.reservation_id = r.id;
    v_deja := coalesce(v_deja, array[]::text[]);
    v_jours := r.arrivee - v_jour;
    v_etape := null;
    if not ('bienvenue' = any(v_deja)) then v_etape := 'bienvenue';
    elsif v_dernier is not null and v_dernier > p_maintenant - interval '6 hours' then v_etape := null;
    elsif v_jours <= g.jours_rappel and not ('rappel' = any(v_deja)) then v_etape := 'rappel';
    elsif v_jours <= g.jours_guide and v_jours > g.jours_rappel and not ('guide' = any(v_deja)) then v_etape := 'guide';
    end if;
    continue when v_etape is null;
    v_note := null;
    if g.whatsapp_actif and nullif(trim(r.whatsapp), '') is not null then v_canal := 'whatsapp';
    elsif r.source_id like 'ht\_%' then v_canal := 'plateforme';
    else v_canal := 'aucun'; v_note := 'Aucun canal d''envoi pour cette réservation';
    end if;
    v_fiche := case when r.ctoken is not null and coalesce(r.cstatut, '') <> 'rempli' then g.url_base || '#checkin=' || r.ctoken else '' end;
    v_app := case when r.acces_voyageur is not null then g.url_base || 'sejour/#/sejour/' || r.acces_voyageur else '' end;
    if v_etape = 'bienvenue' and v_canal = 'plateforme' and r.canal = 'airbnb' and not g.lien_bienvenue_airbnb then
      v_fiche := ''; v_note := 'Airbnb : bienvenue sans lien';
    end if;
    v_val := jsonb_build_object('prenom', split_part(coalesce(nullif(trim(r.vnom), ''), ''), ' ', 1), 'bien', coalesce(r.bnom, ''),
      'arrivee', to_char(r.arrivee, v_fmt), 'depart', to_char(r.depart, v_fmt), 'lien_fiche', v_fiche, 'lien_app', v_app);
    v_langue := lower(left(coalesce(r.langue, ''), 2));
    if v_langue in ('fr', 'en') then
      v_txt := parcours_composer(v_textes->v_etape->>v_langue, v_val);
    else
      v_txt := parcours_composer(v_textes->v_etape->>'fr', v_val) || E'\n\n— — —\n\n' || parcours_composer(v_textes->v_etape->>'en', v_val);
    end if;
    reservation_id := r.id; voyageur := r.vnom; bien := r.bnom; arrivee := r.arrivee;
    etape := v_etape; canal := v_canal; texte := v_txt; note := v_note;
    return next;
  end loop;
end $f$;
revoke all on function parcours_plan_interne(uuid, timestamptz) from public, anon, authenticated;

-- Aperçu pour l'équipe : ce qui partirait maintenant.
create or replace function parcours_apercu(p_tenant uuid)
returns table (reservation_id uuid, voyageur text, bien text, arrivee date, etape text, canal text, texte text, note text)
language plpgsql stable security definer set search_path = public, auth as $f$
begin
  if not app_is_member(p_tenant) then raise exception 'Accès refusé'; end if;
  return query select * from parcours_plan_interne(p_tenant, now());
end $f$;
revoke all on function parcours_apercu(uuid) from public, anon;
grant execute on function parcours_apercu(uuid) to authenticated;

-- L'envoi lui-même, lancé par la tâche programmée.
create or replace function parcours_executer() returns jsonb
language plpgsql security definer set search_path = public, net, extensions as $f$
declare g parcours_reglage; p record; v_heure int; v_req bigint; v_msg uuid; v_n int := 0; v_err int := 0; v_cle text;
  v_canal_msg text; x record; v_ok boolean;
begin
  -- 1) Contrôle des envois précédents : la réponse du pont arrive après coup.
  for x in select e.id, e.requete_id, e.message_id from parcours_envoi e
            where e.statut = 'envoye' and not e.verifie and e.requete_id is not null and e.cree_le < now() - interval '1 minute' loop
    declare rep record;
    begin
      select h.status_code, h.content, h.timed_out, h.error_msg into rep from net._http_response h where h.id = x.requete_id;
      if not found then
        if exists (select 1 from parcours_envoi e where e.id = x.id and e.cree_le < now() - interval '6 hours') then
          update parcours_envoi set verifie = true, detail = 'Réponse du pont non retrouvée' where id = x.id;
        end if;
      else
        v_ok := rep.status_code between 200 and 299 and coalesce(rep.timed_out, false) = false
                and coalesce(rep.content, '') !~ '"ok"\s*:\s*false';
        if v_ok then update parcours_envoi set verifie = true where id = x.id;
        else
          update parcours_envoi set verifie = true, statut = 'erreur',
                 detail = left(coalesce(rep.error_msg, 'Code ' || rep.status_code || ' : ' || coalesce(rep.content, '')), 500) where id = x.id;
          v_err := v_err + 1;
        end if;
      end if;
    end;
  end loop;
  -- 2) Envois dus.
  for g in select * from parcours_reglage where actif loop
    v_heure := extract(hour from (now() at time zone g.fuseau))::int;
    continue when v_heure < g.heure_debut or v_heure >= g.heure_fin;
    for p in select * from parcours_plan_interne(g.tenant_id, now()) loop
      continue when p.canal = 'aucun' or p.canal = 'whatsapp';
      if g.pont_url is null then
        insert into parcours_envoi (tenant_id, reservation_id, etape, canal, statut, detail, verifie)
        values (g.tenant_id, p.reservation_id, p.etape, p.canal, 'erreur', 'Adresse du pont non réglée', true)
        on conflict (reservation_id, etape) do nothing;
        v_err := v_err + 1; continue;
      end if;
      v_cle := current_setting('app.settings.service_role_key', true);
      select net.http_post(url := g.pont_url,
               headers := jsonb_build_object('Content-Type', 'application/json', 'Authorization', 'Bearer ' || coalesce(v_cle, '')),
               body := jsonb_build_object('action', 'sendMessage', 'tenant_id', g.tenant_id,
                         'params', jsonb_build_object('reservationId', substr(r.source_id, 4), 'message', p.texte)))
        into v_req from reservation r where r.id = p.reservation_id;
      select coalesce((select e.enumlabel from pg_enum e join pg_type t on t.oid = e.enumtypid
                        where t.typname = 'canal_message' and e.enumlabel = r.canal::text), 'plateforme')
        into v_canal_msg from reservation r where r.id = p.reservation_id;
      execute format('insert into message (tenant_id, reservation_id, voyageur_id, canal, sens, corps, statut, envoye_le)
                      select r.tenant_id, r.id, r.voyageur_id, %L, ''sortant'', $1, ''envoye'', now() from reservation r where r.id = $2 returning id', v_canal_msg)
        into v_msg using p.texte, p.reservation_id;
      insert into parcours_envoi (tenant_id, reservation_id, etape, canal, statut, requete_id, message_id, detail)
      values (g.tenant_id, p.reservation_id, p.etape, p.canal, 'envoye', v_req, v_msg, p.note)
      on conflict (reservation_id, etape) do nothing;
      if p.etape = 'rappel' then
        insert into parcours_envoi (tenant_id, reservation_id, etape, canal, statut, detail, verifie)
        values (g.tenant_id, p.reservation_id, 'guide', p.canal, 'saute', 'Réservation trop proche de l''arrivée : rappel envoyé directement', true)
        on conflict (reservation_id, etape) do nothing;
      end if;
      v_n := v_n + 1;
    end loop;
  end loop;
  return jsonb_build_object('envoyes', v_n, 'erreurs', v_err);
end $f$;
revoke all on function parcours_executer() from public, anon, authenticated;

-- Une ligne de réglage par société, éteinte.
insert into parcours_reglage (tenant_id) select id from tenant on conflict (tenant_id) do nothing;
