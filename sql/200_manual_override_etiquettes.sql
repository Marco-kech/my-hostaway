-- LOT 1.1 : manual_override sur reservation, bien, tache
-- Flag JSONB pour empêcher l'écrasement des valeurs saisies manuellement

ALTER TABLE reservation ADD COLUMN IF NOT EXISTS manual_override JSONB DEFAULT '{}'::jsonb;
ALTER TABLE bien ADD COLUMN IF NOT EXISTS manual_override JSONB DEFAULT '{}'::jsonb;
ALTER TABLE tache ADD COLUMN IF NOT EXISTS manual_override JSONB DEFAULT '{}'::jsonb;

-- LOT 1.2 : Étiquettes d'annonces (tags)
CREATE TABLE IF NOT EXISTS etiquette (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  nom VARCHAR(25) NOT NULL,
  couleur VARCHAR(7) DEFAULT '#C9A227',
  cree_le TIMESTAMPTZ DEFAULT now(),
  UNIQUE(tenant_id, nom)
);

CREATE TABLE IF NOT EXISTS bien_etiquette (
  bien_id UUID NOT NULL REFERENCES bien(id) ON DELETE CASCADE,
  etiquette_id UUID NOT NULL REFERENCES etiquette(id) ON DELETE CASCADE,
  PRIMARY KEY (bien_id, etiquette_id)
);

-- Index pour le filtrage rapide
CREATE INDEX IF NOT EXISTS idx_etiquette_tenant ON etiquette(tenant_id);
CREATE INDEX IF NOT EXISTS idx_bien_etiquette_bien ON bien_etiquette(bien_id);
CREATE INDEX IF NOT EXISTS idx_bien_etiquette_etiq ON bien_etiquette(etiquette_id);

-- RLS
ALTER TABLE etiquette ENABLE ROW LEVEL SECURITY;
ALTER TABLE bien_etiquette ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS etiquette_tenant ON etiquette;
CREATE POLICY etiquette_tenant ON etiquette FOR ALL USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

DROP POLICY IF EXISTS bien_etiquette_tenant ON bien_etiquette;
CREATE POLICY bien_etiquette_tenant ON bien_etiquette FOR ALL
  USING (bien_id IN (SELECT id FROM bien WHERE tenant_id = current_setting('app.tenant_id', true)::uuid));

-- LOT 1.3 : Héritage — snapshot financier figé à la création de la réservation
ALTER TABLE reservation ADD COLUMN IF NOT EXISTS financier_fige JSONB DEFAULT '{}'::jsonb;

-- Champs supplémentaires pour l'héritage
ALTER TABLE bien ADD COLUMN IF NOT EXISTS prix_personne_supp NUMERIC DEFAULT 0;
ALTER TABLE bien ADD COLUMN IF NOT EXISTS remise_hebdo_pct NUMERIC DEFAULT 0;
ALTER TABLE bien ADD COLUMN IF NOT EXISTS remise_hebdo_seuil INTEGER DEFAULT 7;
ALTER TABLE bien ADD COLUMN IF NOT EXISTS remise_mensuelle_pct NUMERIC DEFAULT 0;
ALTER TABLE bien ADD COLUMN IF NOT EXISTS remise_mensuelle_seuil INTEGER DEFAULT 30;
ALTER TABLE bien ADD COLUMN IF NOT EXISTS frais_standards JSONB DEFAULT '[]'::jsonb;
ALTER TABLE bien ADD COLUMN IF NOT EXISTS majoration_canaux JSONB DEFAULT '{}'::jsonb;

-- Champs financiers détaillés sur la réservation
ALTER TABLE reservation ADD COLUMN IF NOT EXISTS base_rate NUMERIC;
ALTER TABLE reservation ADD COLUMN IF NOT EXISTS frais_detail JSONB DEFAULT '[]'::jsonb;
ALTER TABLE reservation ADD COLUMN IF NOT EXISTS taxes_detail JSONB DEFAULT '[]'::jsonb;
ALTER TABLE reservation ADD COLUMN IF NOT EXISTS commission_canal_pct NUMERIC DEFAULT 0;
ALTER TABLE reservation ADD COLUMN IF NOT EXISTS sous_total NUMERIC;
ALTER TABLE reservation ADD COLUMN IF NOT EXISTS total_taxes NUMERIC;
ALTER TABLE reservation ADD COLUMN IF NOT EXISTS total_frais NUMERIC;
ALTER TABLE reservation ADD COLUMN IF NOT EXISTS raison_annulation TEXT;

-- LOT 2 : Frais personnalisés et ventes incitatives sur le bien
ALTER TABLE bien ADD COLUMN IF NOT EXISTS frais_personnalises JSONB DEFAULT '[]'::jsonb;
ALTER TABLE bien ADD COLUMN IF NOT EXISTS ventes_incitatives JSONB DEFAULT '[]'::jsonb;
ALTER TABLE bien ADD COLUMN IF NOT EXISTS politique_annulation_canaux JSONB DEFAULT '{}'::jsonb;

-- Statut séjour propriétaire
-- (ajouter 'sejour_proprietaire' aux statuts possibles - pas de contrainte enum en base)
