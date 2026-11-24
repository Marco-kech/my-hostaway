-- Correctifs du 25 nov. 2026 : colonnes manquantes + règles de sécurité des étiquettes alignées sur le reste de l'app
ALTER TABLE reservation ADD COLUMN IF NOT EXISTS heure_checkin time;
ALTER TABLE reservation ADD COLUMN IF NOT EXISTS heure_checkout time;
ALTER TABLE modele_checklist ADD COLUMN IF NOT EXISTS type text;
ALTER TABLE modele_checklist ADD COLUMN IF NOT EXISTS bien_id uuid REFERENCES bien(id) ON DELETE SET NULL;

DROP POLICY IF EXISTS etiquette_tenant ON etiquette;
CREATE POLICY etiquette_tenant ON etiquette FOR ALL USING (app_is_member(tenant_id)) WITH CHECK (app_is_member(tenant_id));
DROP POLICY IF EXISTS bien_etiquette_tenant ON bien_etiquette;
CREATE POLICY bien_etiquette_tenant ON bien_etiquette FOR ALL
  USING (bien_id IN (SELECT id FROM bien WHERE app_is_member(tenant_id)))
  WITH CHECK (bien_id IN (SELECT id FROM bien WHERE app_is_member(tenant_id)));
