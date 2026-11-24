-- 220 — Page d'avis du voyageur (lien unique par réservation, comme le {{review_url}} de Hostaway).
-- Ajout pur. La page ne connaît la réservation que par le lien voyageur (reservation.acces_voyageur).

create or replace function avis_infos(p_token text) returns jsonb
language sql stable security definer set search_path = public as $f$
  select jsonb_build_object('bien', b.nom, 'arrivee', r.arrivee, 'depart', r.depart,
           'deja', exists (select 1 from avis a where a.reservation_id = r.id and a.origine = 'direct'))
  from reservation r left join bien b on b.id = r.bien_id
  where p_token is not null and length(p_token) >= 16 and r.acces_voyageur = p_token limit 1;
$f$;

create or replace function avis_deposer(p_token text, p_infos jsonb) returns text
language plpgsql security definer set search_path = public as $f$
declare r record; v_note numeric;
  v_re constant text := '^[1-5]$';
begin
  if p_token is null or length(p_token) < 16 then return 'invalide'; end if;
  select id, tenant_id, bien_id, voyageur_id into r from reservation where acces_voyageur = p_token limit 1;
  if r.id is null then return 'invalide'; end if;
  if exists (select 1 from avis a where a.reservation_id = r.id and a.origine = 'direct') then return 'deja_depose'; end if;
  if coalesce(p_infos->>'note_globale', '') !~ v_re then raise exception 'La note globale est obligatoire'; end if;
  v_note := (p_infos->>'note_globale')::numeric;
  insert into avis (tenant_id, reservation_id, bien_id, voyageur_id, canal, origine, statut, afficher_site,
                    note_globale, note_proprete, note_communication, note_emplacement, note_qualite_prix, commentaire)
  values (r.tenant_id, r.id, r.bien_id, r.voyageur_id, 'direct', 'direct', 'publie', true, v_note,
          case when p_infos->>'note_proprete' ~ v_re then (p_infos->>'note_proprete')::numeric end,
          case when p_infos->>'note_communication' ~ v_re then (p_infos->>'note_communication')::numeric end,
          case when p_infos->>'note_emplacement' ~ v_re then (p_infos->>'note_emplacement')::numeric end,
          case when p_infos->>'note_qualite_prix' ~ v_re then (p_infos->>'note_qualite_prix')::numeric end,
          left(nullif(trim(p_infos->>'commentaire'), ''), 4000));
  return 'ok';
end $f$;

revoke all on function avis_infos(text) from public;
revoke all on function avis_deposer(text, jsonb) from public;
grant execute on function avis_infos(text) to anon, authenticated;
grant execute on function avis_deposer(text, jsonb) to anon, authenticated;
