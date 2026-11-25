-- 240 — Déclencheurs de messages : délai après l'événement + « message reçu » (premier message du voyageur).
-- Toujours des brouillons, jamais d'envoi. Ajout pur.

alter table auto_message_journal add column if not exists prevu_le timestamptz;
alter table auto_message_journal add column if not exists abandonne boolean not null default false;
create index if not exists idx_auto_message_attente on auto_message_journal (prevu_le) where message_id is null and not abandonne;

create or replace function auto_message_preparer(p_tenant uuid, p_resa uuid, p_evenement text, p_source uuid) returns void
language plpgsql security definer set search_path = public as $f$
declare m record; j uuid; mid uuid; v_voy uuid;
begin
  if p_tenant is null or p_resa is null or p_source is null then return; end if;
  select voyageur_id into v_voy from reservation where id = p_resa;
  for m in select id, canal, corps, coalesce(delai_h, 0) as delai from modele_message
            where tenant_id = p_tenant and actif and evenement = p_evenement loop
    j := null;
    insert into auto_message_journal (tenant_id, reservation_id, modele_id, evenement, source_id, prevu_le)
      values (p_tenant, p_resa, m.id, p_evenement, p_source, case when m.delai > 0 then now() + make_interval(hours => m.delai) end)
      on conflict (modele_id, evenement, source_id) do nothing returning id into j;
    if j is null or m.delai > 0 then continue; end if;
    insert into message (tenant_id, reservation_id, voyageur_id, canal, sens, corps, statut)
      values (p_tenant, p_resa, v_voy, m.canal, 'sortant', auto_message_composer(m.corps, p_resa), 'brouillon')
      returning id into mid;
    update auto_message_journal set message_id = mid where id = j;
  end loop;
end $f$;

-- Passe toutes les 15 minutes : crée les brouillons dont le délai est écoulé.
-- Un brouillon en attente est abandonné si la réservation a été annulée entre-temps (sauf pour l'événement « annulation »).
create or replace function auto_message_echeances() returns int
language plpgsql security definer set search_path = public as $f$
declare j record; mid uuid; n int := 0;
begin
  for j in
    select a.id, a.tenant_id, a.reservation_id, a.evenement, mo.canal, mo.corps, mo.actif, r.voyageur_id, r.statut::text as statut
      from auto_message_journal a
      join modele_message mo on mo.id = a.modele_id
      join reservation r on r.id = a.reservation_id
     where a.message_id is null and not a.abandonne and a.prevu_le is not null and a.prevu_le <= now()
     order by a.prevu_le limit 200
     for update of a skip locked
  loop
    begin
      if not j.actif or (j.statut = 'annulee' and j.evenement <> 'annulation') then
        update auto_message_journal set abandonne = true where id = j.id;
        continue;
      end if;
      insert into message (tenant_id, reservation_id, voyageur_id, canal, sens, corps, statut)
        values (j.tenant_id, j.reservation_id, j.voyageur_id, j.canal, 'sortant', auto_message_composer(j.corps, j.reservation_id), 'brouillon')
        returning id into mid;
      update auto_message_journal set message_id = mid where id = j.id;
      n := n + 1;
    exception when others then
      raise warning 'auto_message_echeances : %', sqlerrm;
    end;
  end loop;
  return n;
end $f$;

create or replace function auto_message_recu() returns trigger
language plpgsql security definer set search_path = public as $f$
begin
  begin
    if new.sens::text = 'entrant' and new.reservation_id is not null
       and not exists (select 1 from message x where x.reservation_id = new.reservation_id
                        and x.sens::text = 'entrant' and x.id <> new.id and x.cree_le < new.cree_le) then
      perform auto_message_preparer(new.tenant_id, new.reservation_id, 'message_recu', new.reservation_id);
    end if;
  exception when others then
    raise warning 'auto_message_recu : %', sqlerrm;
  end;
  return null;
end $f$;

drop trigger if exists zz_auto_message_recu on message;
create trigger zz_auto_message_recu after insert on message
  for each row execute function auto_message_recu();

revoke all on function auto_message_preparer(uuid, uuid, text, uuid) from public, anon, authenticated;
revoke all on function auto_message_echeances() from public, anon, authenticated;

do $c$
begin
  if exists (select 1 from cron.job where jobname = 'auto-message-echeances') then
    perform cron.unschedule('auto-message-echeances');
  end if;
  perform cron.schedule('auto-message-echeances', '*/15 * * * *', 'select public.auto_message_echeances()');
end $c$;
