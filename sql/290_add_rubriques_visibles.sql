-- Ajout colonne rubriques_visibles à la table membre (pour gestion collaborateurs)
-- Si la colonne existe déjà, cette commande est ignorée gracieusement.
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='membre' AND column_name='rubriques_visibles') THEN
    ALTER TABLE membre ADD COLUMN rubriques_visibles text[] DEFAULT NULL;
    COMMENT ON COLUMN membre.rubriques_visibles IS 'Liste des rubriques visibles par ce collaborateur. NULL = administrateur complet (tout voir).';
  END IF;
END $$;
