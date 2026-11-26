-- Multi-unités : un bien parent peut avoir N sous-unités (chambres)
-- Chaque sous-unité a son propre nom, tarif, et peut recevoir des réservations

-- Table des sous-unités
create table if not exists bien_unite (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenant(id),
  bien_id uuid not null references bien(id) on delete cascade,
  nom text not null default 'Unité',
  ordre int not null default 0,
  prix_nuit numeric,
  actif boolean not null default true,
  cree_le timestamptz not null default now()
);

-- Colonne sur reservation pour savoir quelle unité est occupée
alter table reservation add column if not exists unite_id uuid references bien_unite(id);

-- Colonne sur bien pour le nombre d'unités (shortcut)
alter table bien add column if not exists nb_unites int;

-- Chambres à vendre par période (réduire la dispo)
create table if not exists unite_restriction (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenant(id),
  bien_id uuid not null references bien(id) on delete cascade,
  debut date not null,
  fin date not null,
  chambres_vendables int not null default 0,
  cree_le timestamptz not null default now()
);

-- RLS
alter table bien_unite enable row level security;
drop policy if exists bien_unite_sel on bien_unite;
create policy bien_unite_sel on bien_unite for select using (app_is_member(tenant_id));
drop policy if exists bien_unite_ins on bien_unite;
create policy bien_unite_ins on bien_unite for insert with check (app_is_member(tenant_id));
drop policy if exists bien_unite_upd on bien_unite;
create policy bien_unite_upd on bien_unite for update using (app_is_member(tenant_id));
drop policy if exists bien_unite_del on bien_unite;
create policy bien_unite_del on bien_unite for delete using (app_is_member(tenant_id));

alter table unite_restriction enable row level security;
drop policy if exists unite_restriction_sel on unite_restriction;
create policy unite_restriction_sel on unite_restriction for select using (app_is_member(tenant_id));
drop policy if exists unite_restriction_ins on unite_restriction;
create policy unite_restriction_ins on unite_restriction for insert with check (app_is_member(tenant_id));
drop policy if exists unite_restriction_upd on unite_restriction;
create policy unite_restriction_upd on unite_restriction for update using (app_is_member(tenant_id));
drop policy if exists unite_restriction_del on unite_restriction;
create policy unite_restriction_del on unite_restriction for delete using (app_is_member(tenant_id));

-- Fonction : attribution automatique d'une unité libre pour une réservation
create or replace function attribuer_unite(p_bien_id uuid, p_arrivee date, p_depart date)
returns uuid language plpgsql stable security definer set search_path = public as $f$
declare u record; pris uuid[];
begin
  -- Trouver les unités déjà prises sur cette période
  select array_agg(distinct r.unite_id) into pris
    from reservation r
   where r.bien_id = p_bien_id and r.unite_id is not null
     and r.statut::text not in ('annulee','no_show')
     and r.arrivee < p_depart and r.depart > p_arrivee;
  
  -- Trouver une unité libre au hasard
  for u in
    select bu.id from bien_unite bu
     where bu.bien_id = p_bien_id and bu.actif
       and (pris is null or bu.id <> all(pris))
     order by random() limit 1
  loop
    return u.id;
  end loop;
  
  return null; -- toutes occupées
end $f$;

revoke all on function attribuer_unite(uuid, date, date) from public, anon;
grant execute on function attribuer_unite(uuid, date, date) to authenticated;
