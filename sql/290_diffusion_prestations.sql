-- 210 — Visibilité des prestations en trois choix : application, site, application et site.
-- Ajout seulement : aucune colonne ni donnée supprimée. L'ancien oui/non « visible_site » reste et suit le nouveau réglage.
-- Rejouable. Retour arrière : 219_diffusion_retour_arriere.sql.

alter table prestation add column if not exists diffusion text not null default 'application';
alter table bien_prestation add column if not exists diffusion text not null default 'application';
do $$ begin
  if not exists (select 1 from pg_constraint where conname = 'prestation_diffusion_chk') then
    alter table prestation add constraint prestation_diffusion_chk check (diffusion in ('application','site','application et site'));
  end if;
  if not exists (select 1 from pg_constraint where conname = 'bien_prestation_diffusion_chk') then
    alter table bien_prestation add constraint bien_prestation_diffusion_chk check (diffusion in ('application','site','application et site'));
  end if;
end $$;

-- Reprise de l'existant : ce qui était « visible sur le site » devient « application et site ».
update prestation set diffusion = 'application et site' where visible_site and diffusion = 'application';
update bien_prestation set diffusion = 'application et site' where visible_site and diffusion = 'application';

-- Les deux réglages restent d'accord, quel que soit l'écran qui écrit (nouveau ou ancien).
-- Sur une prestation, seul un membre de l'équipe change la visibilité (comme avant pour visible_site).
create or replace function cg_diffusion_accord() returns trigger
language plpgsql security definer set search_path = public, auth as $$
declare v_equipe boolean := auth.uid() is null or app_is_member(new.tenant_id);
begin
  if tg_op = 'INSERT' then
    if new.diffusion = 'application' and new.visible_site then new.diffusion := 'application et site'; end if;
  elsif new.diffusion is not distinct from old.diffusion and new.visible_site is distinct from old.visible_site then
    new.diffusion := case when new.visible_site then 'application et site' else 'application' end;
  end if;
  if tg_table_name = 'prestation' and not v_equipe then
    if tg_op = 'INSERT' and new.diffusion <> 'application' then
      raise exception 'La visibilité sur le site est fixée par la conciergerie';
    elsif tg_op = 'UPDATE' and new.diffusion is distinct from old.diffusion then
      raise exception 'La visibilité sur le site est fixée par la conciergerie';
    end if;
  end if;
  new.visible_site := (new.diffusion <> 'application');
  return new;
end $$;
revoke all on function cg_diffusion_accord() from public, anon, authenticated;

drop trigger if exists trg_cg_a_diffusion on prestation;
create trigger trg_cg_a_diffusion before insert or update on prestation
  for each row execute function cg_diffusion_accord();
drop trigger if exists trg_cg_a_diffusion on bien_prestation;
create trigger trg_cg_a_diffusion before insert or update on bien_prestation
  for each row execute function cg_diffusion_accord();

-- Application du voyageur : une prestation réglée « site » seulement n'y apparaît pas.
create or replace function cg_prestations_du_bien(p_bien uuid) returns setof prestation
language sql stable security definer set search_path = public as $$
  select p.* from prestation p join bien b on b.id = p_bien
  where p.tenant_id = b.tenant_id and p.actif
    and (p.au_logement or p.a_l_exterieur)
    and (p.type = 'dpm'
         or (p.type = 'interne' and p.proprietaire_id = b.proprietaire_id)
         or (p.type = 'externe' and exists (select 1 from partenaire pa where pa.id = p.partenaire_id and pa.actif)))
    and ((not exists (select 1 from bien_prestation bp where bp.bien_id = b.id) and p.diffusion <> 'site')
         or exists (select 1 from bien_prestation bp where bp.bien_id = b.id and bp.prestation_id = p.id and bp.diffusion <> 'site'));
$$;
revoke all on function cg_prestations_du_bien(uuid) from public, anon, authenticated;

-- Site WordPress : la liste à afficher pour un bien (servira à l'export vers le site).
create or replace function cg_prestations_site_du_bien(p_bien uuid) returns setof prestation
language sql stable security definer set search_path = public as $$
  select p.* from prestation p join bien b on b.id = p_bien
  where p.tenant_id = b.tenant_id and p.actif
    and (p.au_logement or p.a_l_exterieur)
    and (p.type = 'dpm'
         or (p.type = 'interne' and p.proprietaire_id = b.proprietaire_id)
         or (p.type = 'externe' and exists (select 1 from partenaire pa where pa.id = p.partenaire_id and pa.actif)))
    and ((not exists (select 1 from bien_prestation bp where bp.bien_id = b.id) and p.diffusion <> 'application')
         or exists (select 1 from bien_prestation bp where bp.bien_id = b.id and bp.prestation_id = p.id and bp.diffusion <> 'application'));
$$;
revoke all on function cg_prestations_site_du_bien(uuid) from public, anon, authenticated;
