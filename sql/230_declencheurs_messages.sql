-- 230 — Déclencheurs de messages façon Hostaway : un événement prépare un BROUILLON dans Conversations.
-- Rien n'est envoyé au voyageur : le brouillon se relit et s'envoie à la main, comme pour « Préparer les messages ».
-- Ajout pur. Chaque déclencheur est protégé : s'il échoue, l'opération d'origine (réservation, paiement…) passe quand même.

create table if not exists auto_message_journal (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenant(id) on delete cascade,
  reservation_id uuid references reservation(id) on delete cascade,
  modele_id uuid not null references modele_message(id) on delete cascade,
  evenement text not null,
  source_id uuid not null,
  message_id uuid,
  cree_le timestamptz not null default now(),
  unique (modele_id, evenement, source_id)
);
alter table auto_message_journal enable row level security;
drop policy if exists auto_message_journal_lecture on auto_message_journal;
create policy auto_message_journal_lecture on auto_message_journal for select to authenticated using (app_is_member(tenant_id));

create or replace function auto_message_composer(p_corps text, p_resa uuid) returns text
language plpgsql stable security definer set search_path = public as $f$
declare r record; t text := coalesce(p_corps, ''); nuits int; k text; v text; vals jsonb;
begin
  select re.arrivee, re.depart, re.prix_total, re.montant_paye, re.canal::text as canal, re.nb_personnes,
         re.reference_canal, re.acces_voyageur, b.nom as bien, b.adresse, coalesce(b.parametres, '{}'::jsonb) as p,
         vo.nom as voyageur, vo.email, vo.tel
    into r
    from reservation re left join bien b on b.id = re.bien_id left join voyageur vo on vo.id = re.voyageur_id
   where re.id = p_resa;
  if not found then return t; end if;
  nuits := greatest(1, coalesce(r.depart - r.arrivee, 1));
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
    'lien_avis', case when r.acces_voyageur is null then '' else 'https://marco-kech.github.io/my-hostaway/avis.html#' || r.acces_voyageur end,
    'date_aujourdhui', to_char(now() at time zone 'Africa/Casablanca', 'DD/MM/YYYY'));
  for k, v in select * from jsonb_each_text(vals) loop
    t := replace(t, '{' || k || '}', v);
  end loop;
  return t;
end $f$;

create or replace function auto_message_preparer(p_tenant uuid, p_resa uuid, p_evenement text, p_source uuid) returns void
language plpgsql security definer set search_path = public as $f$
declare m record; j uuid; mid uuid; v_voy uuid;
begin
  if p_tenant is null or p_resa is null or p_source is null then return; end if;
  select voyageur_id into v_voy from reservation where id = p_resa;
  for m in select id, canal, corps from modele_message where tenant_id = p_tenant and actif and evenement = p_evenement loop
    j := null;
    insert into auto_message_journal (tenant_id, reservation_id, modele_id, evenement, source_id)
      values (p_tenant, p_resa, m.id, p_evenement, p_source)
      on conflict (modele_id, evenement, source_id) do nothing returning id into j;
    if j is null then continue; end if;
    insert into message (tenant_id, reservation_id, voyageur_id, canal, sens, corps, statut)
      values (p_tenant, p_resa, v_voy, m.canal, 'sortant', auto_message_composer(m.corps, p_resa), 'brouillon')
      returning id into mid;
    update auto_message_journal set message_id = mid where id = j;
  end loop;
end $f$;

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
  exception when others then
    raise warning 'auto_message_resa : %', sqlerrm;
  end;
  return null;
end $f$;

create or replace function auto_message_paiement() returns trigger
language plpgsql security definer set search_path = public as $f$
begin
  begin
    if new.statut::text = 'reussi' and new.montant > 0 then
      perform auto_message_preparer(new.tenant_id, new.reservation_id, 'paiement_recu', new.id);
    end if;
  exception when others then
    raise warning 'auto_message_paiement : %', sqlerrm;
  end;
  return null;
end $f$;

create or replace function auto_message_fiche() returns trigger
language plpgsql security definer set search_path = public as $f$
begin
  begin
    if new.statut = 'rempli' and old.statut is distinct from 'rempli' then
      perform auto_message_preparer(new.tenant_id, new.reservation_id, 'fiche_soumise', new.id);
    end if;
  exception when others then
    raise warning 'auto_message_fiche : %', sqlerrm;
  end;
  return null;
end $f$;

create or replace function auto_message_avis() returns trigger
language plpgsql security definer set search_path = public as $f$
begin
  begin
    if new.origine = 'direct' and new.reservation_id is not null then
      perform auto_message_preparer(new.tenant_id, new.reservation_id, 'avis_soumis', new.id);
    end if;
  exception when others then
    raise warning 'auto_message_avis : %', sqlerrm;
  end;
  return null;
end $f$;

drop trigger if exists auto_message_resa on reservation;
create trigger auto_message_resa after insert or update of statut on reservation
  for each row execute function auto_message_resa();
-- Nommé « zz_ » pour passer après paiement_recalc_ins : le montant payé est alors à jour dans le brouillon.
drop trigger if exists auto_message_paiement on paiement;
drop trigger if exists zz_auto_message_paiement on paiement;
create trigger zz_auto_message_paiement after insert on paiement
  for each row execute function auto_message_paiement();
drop trigger if exists auto_message_fiche on checkin_online;
create trigger auto_message_fiche after update of statut on checkin_online
  for each row execute function auto_message_fiche();
drop trigger if exists auto_message_avis on avis;
create trigger auto_message_avis after insert on avis
  for each row execute function auto_message_avis();

revoke all on function auto_message_composer(text, uuid) from public, anon, authenticated;
revoke all on function auto_message_preparer(uuid, uuid, text, uuid) from public, anon, authenticated;
