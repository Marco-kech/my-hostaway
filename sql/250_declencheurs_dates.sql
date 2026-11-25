-- 250 — Événements liés aux dates (avant l'arrivée, arrivée, départ, après le départ, réservation) :
-- préparation automatique du brouillon à l'échéance, en tenant compte du délai du modèle.
-- Éteint par défaut : rien ne change tant que le réglage « auto_messages.dates » n'est pas activé dans l'application.
-- Toujours des brouillons, jamais d'envoi. Ajout pur.

create or replace function auto_message_dates_actif(p_tenant uuid) returns boolean
language sql stable security definer set search_path = public as $f$
  select coalesce((select (valeur::jsonb ->> 'dates') = 'true' from reglage where tenant_id = p_tenant and cle = 'auto_messages' limit 1), false);
$f$;

create or replace function auto_message_heure(p text, p_defaut text) returns time
language sql immutable as $f$
  select case when p ~ '^([01][0-9]|2[0-3]):[0-5][0-9]' then left(p, 5)::time else p_defaut::time end;
$f$;

-- Délai du modèle : « avant l'arrivée » = heures avant ; « après le départ » = heures après ;
-- « arrivée » et « départ » = heures après (valeur négative = avant).
create or replace function auto_message_dates() returns int
language plpgsql security definer set search_path = public as $f$
declare c record; j uuid; mid uuid; n int := 0;
begin
  for c in
    with base as (
      select mo.id as modele_id, mo.tenant_id, mo.evenement, mo.canal, mo.corps, coalesce(mo.delai_h, 0) as d,
             r.id as resa, r.voyageur_id,
             ((r.arrivee + coalesce(r.heure_checkin, auto_message_heure(b.parametres ->> 'heure_arrivee', '15:00')))::timestamp
                at time zone coalesce(g.fuseau, 'Africa/Casablanca')) as t_arr,
             ((r.depart + coalesce(r.heure_checkout, auto_message_heure(b.parametres ->> 'heure_depart', '11:00')))::timestamp
                at time zone coalesce(g.fuseau, 'Africa/Casablanca')) as t_dep
        from modele_message mo
        join reservation r on r.tenant_id = mo.tenant_id
        left join bien b on b.id = r.bien_id
        left join parcours_reglage g on g.tenant_id = mo.tenant_id
       where mo.actif and mo.evenement in ('avant_arrivee', 'arrivee', 'depart', 'apres_depart')
         and auto_message_dates_actif(mo.tenant_id)
         and r.statut::text in ('confirmee', 'terminee')
         and r.depart >= current_date - 3 and r.arrivee <= current_date + 400
    ), prevu as (
      select base.*, case evenement
               when 'avant_arrivee' then t_arr - make_interval(hours => abs(d))
               when 'arrivee' then t_arr + make_interval(hours => d)
               when 'depart' then t_dep + make_interval(hours => d)
               else t_dep + make_interval(hours => abs(d)) end as echeance
        from base
    )
    select * from prevu p
     where p.echeance <= now()
       and ((p.evenement = 'avant_arrivee' and now() < p.t_arr)
            or (p.evenement <> 'avant_arrivee' and p.echeance > now() - interval '24 hours'))
       and not exists (select 1 from auto_message_journal a
                        where a.modele_id = p.modele_id and a.evenement = p.evenement and a.source_id = p.resa)
     limit 300
  loop
    begin
      j := null;
      insert into auto_message_journal (tenant_id, reservation_id, modele_id, evenement, source_id)
        values (c.tenant_id, c.resa, c.modele_id, c.evenement, c.resa)
        on conflict (modele_id, evenement, source_id) do nothing returning id into j;
      if j is null then continue; end if;
      insert into message (tenant_id, reservation_id, voyageur_id, canal, sens, corps, statut)
        values (c.tenant_id, c.resa, c.voyageur_id, c.canal, 'sortant', auto_message_composer(c.corps, c.resa), 'brouillon')
        returning id into mid;
      update auto_message_journal set message_id = mid where id = j;
      n := n + 1;
    exception when others then
      raise warning 'auto_message_dates : %', sqlerrm;
    end;
  end loop;
  return n;
end $f$;

-- Réservation : même fonction qu'avant, plus l'événement « réservation » à la confirmation (si le réglage est activé).
create or replace function auto_message_resa() returns trigger
language plpgsql security definer set search_path = public as $f$
declare ev text;
begin
  begin
    if tg_op = 'UPDATE' and new.statut is not distinct from old.statut then return null; end if;
    ev := case new.statut::text when 'annulee' then 'annulation' when 'en_attente' then 'reservation_attente'
                                when 'demande' then 'demande_invite' end;
    if ev is not null and (tg_op = 'UPDATE' or ev <> 'annulation') then
      perform auto_message_preparer(new.tenant_id, new.id, ev, new.id);
    end if;
    if new.statut::text = 'confirmee' and new.depart >= current_date and auto_message_dates_actif(new.tenant_id) then
      perform auto_message_preparer(new.tenant_id, new.id, 'reservation', new.id);
    end if;
  exception when others then
    raise warning 'auto_message_resa : %', sqlerrm;
  end;
  return null;
end $f$;

-- À l'activation, l'application signale les brouillons déjà préparés à la main pour éviter les doublons.
create or replace function auto_message_marquer(p_paires jsonb) returns int
language plpgsql security definer set search_path = public as $f$
declare e jsonb; mo record; n int := 0; k int;
begin
  for e in select * from jsonb_array_elements(coalesce(p_paires, '[]'::jsonb)) loop
    select id, tenant_id, evenement into mo from modele_message where id = (e ->> 'm')::uuid;
    if mo.id is null or not app_is_member(mo.tenant_id) then continue; end if;
    insert into auto_message_journal (tenant_id, reservation_id, modele_id, evenement, source_id, abandonne)
      select mo.tenant_id, r.id, mo.id, mo.evenement, r.id, true from reservation r
       where r.id = (e ->> 'r')::uuid and r.tenant_id = mo.tenant_id
      on conflict (modele_id, evenement, source_id) do nothing;
    get diagnostics k = row_count; n := n + k;
  end loop;
  return n;
end $f$;

revoke all on function auto_message_dates() from public, anon, authenticated;
revoke all on function auto_message_dates_actif(uuid) from public, anon, authenticated;
revoke all on function auto_message_marquer(jsonb) from public, anon;
grant execute on function auto_message_marquer(jsonb) to authenticated;

do $c$
begin
  if exists (select 1 from cron.job where jobname = 'auto-message-echeances') then
    perform cron.unschedule('auto-message-echeances');
  end if;
  perform cron.schedule('auto-message-echeances', '*/15 * * * *', 'select public.auto_message_echeances(), public.auto_message_dates()');
end $c$;
