-- ============================================================
-- Fonctions RPC publiques pour le site WordPress
-- dpmconciergerie-group.com → My Hostaway (Supabase)
-- Exécuté le 26 nov. 2026
-- ============================================================

-- 1. Catalogue public des upsells pour un bien donné
CREATE OR REPLACE FUNCTION public.upsells_catalogue(p_bien_id uuid)
RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER
AS $$
DECLARE
  v_bien record;
  v_result jsonb;
  v_has_custom boolean;
BEGIN
  SELECT id, nom, proprietaire_id INTO v_bien
  FROM bien WHERE id = p_bien_id;
  IF NOT FOUND THEN
    RETURN jsonb_build_object('error', 'Bien introuvable');
  END IF;

  SELECT EXISTS(
    SELECT 1 FROM bien_prestation WHERE bien_id = p_bien_id
  ) INTO v_has_custom;

  SELECT jsonb_build_object(
    'bien_id', p_bien_id,
    'bien_nom', v_bien.nom,
    'prestations', COALESCE(jsonb_agg(
      jsonb_build_object(
        'id', p.id,
        'nom', p.nom,
        'categorie', COALESCE(p.categorie, 'Autres'),
        'icone', COALESCE(p.icone, ''),
        'unite', COALESCE(p.unite, ''),
        'description', COALESCE(p.description, ''),
        'au_logement', COALESCE(p.au_logement, false),
        'a_l_exterieur', COALESCE(p.a_l_exterieur, false),
        'prix_logement', CASE WHEN COALESCE(p.au_logement, false)
          THEN COALESCE(p.prix_public_logement, p.prix_logement, 0) ELSE NULL END,
        'prix_exterieur', CASE WHEN COALESCE(p.a_l_exterieur, false)
          THEN COALESCE(p.prix_public_exterieur, p.prix_exterieur, 0) ELSE NULL END
      ) ORDER BY p.categorie, p.nom
    ), '[]'::jsonb)
  ) INTO v_result
  FROM prestation p
  WHERE p.actif = true
    AND (p.type != 'interne' OR p.proprietaire_id = v_bien.proprietaire_id)
    AND CASE
      WHEN v_has_custom THEN
        EXISTS(SELECT 1 FROM bien_prestation bp
               WHERE bp.bien_id = p_bien_id
               AND bp.prestation_id = p.id
               AND bp.visible_site = true)
      ELSE
        COALESCE(p.visible_site, false) = true
    END;

  RETURN v_result;
END;
$$;

GRANT EXECUTE ON FUNCTION public.upsells_catalogue(uuid) TO anon;

-- 2. Passer une commande d'upsell depuis le site WordPress
CREATE OR REPLACE FUNCTION public.upsells_commander(
  p_bien_id uuid,
  p_prestation_id uuid,
  p_voyageur_nom text,
  p_voyageur_email text DEFAULT NULL,
  p_voyageur_tel text DEFAULT NULL,
  p_date date DEFAULT CURRENT_DATE,
  p_heure text DEFAULT NULL,
  p_quantite int DEFAULT 1,
  p_note text DEFAULT NULL
)
RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER
AS $$
DECLARE
  v_bien record;
  v_presta record;
  v_voy_id uuid;
  v_qty int;
  v_montant numeric;
  v_part_conciergerie numeric;
  v_reversement numeric;
  v_part_proprietaire numeric;
  v_statut text;
  v_cmd_id uuid;
BEGIN
  SELECT id, tenant_id, nom INTO v_bien
  FROM bien WHERE id = p_bien_id;
  IF NOT FOUND THEN
    RETURN jsonb_build_object('error', 'Bien introuvable');
  END IF;

  SELECT * INTO v_presta
  FROM prestation WHERE id = p_prestation_id AND actif = true;
  IF NOT FOUND THEN
    RETURN jsonb_build_object('error', 'Prestation introuvable ou inactive');
  END IF;

  IF p_voyageur_email IS NOT NULL AND p_voyageur_email != '' THEN
    SELECT id INTO v_voy_id
    FROM voyageur
    WHERE tenant_id = v_bien.tenant_id AND email = p_voyageur_email
    LIMIT 1;

    IF v_voy_id IS NULL THEN
      INSERT INTO voyageur(tenant_id, nom, email, tel, source)
      VALUES(v_bien.tenant_id, p_voyageur_nom, p_voyageur_email, p_voyageur_tel, 'site_web')
      RETURNING id INTO v_voy_id;
    END IF;
  END IF;

  v_qty := GREATEST(1, COALESCE(p_quantite, 1));
  v_montant := COALESCE(v_presta.prix_logement, v_presta.prix_exterieur, 0) * v_qty;
  v_reversement := COALESCE(v_presta.net_partenaire, 0) * v_qty;
  v_part_proprietaire := 0;

  IF v_presta.type = 'externe' THEN
    v_part_conciergerie := v_montant - v_reversement;
  ELSIF v_presta.type = 'interne' THEN
    IF COALESCE(v_presta.mode_commission_logement, 'pct') = 'pct' THEN
      v_part_conciergerie := ROUND(v_montant * COALESCE(v_presta.commission_logement, 0) / 100);
    ELSE
      v_part_conciergerie := COALESCE(v_presta.commission_logement, 0) * v_qty;
    END IF;
    v_part_proprietaire := v_montant - v_part_conciergerie;
    v_reversement := 0;
  ELSE
    v_part_conciergerie := v_montant;
    v_reversement := 0;
  END IF;

  v_statut := CASE WHEN COALESCE(v_presta.validation, 'auto') = 'auto' THEN 'confirme' ELSE 'attente' END;

  INSERT INTO commande(tenant_id, bien_id, prestation_id, voyageur_id, date, heure,
    quantite, montant, part_conciergerie, reversement, part_proprietaire,
    statut, reglement, source, note)
  VALUES(v_bien.tenant_id, p_bien_id, p_prestation_id, v_voy_id, p_date, p_heure,
    v_qty, v_montant, v_part_conciergerie, v_reversement, v_part_proprietaire,
    v_statut, 'non', 'site_web',
    CASE WHEN p_note IS NOT NULL THEN '[Site web] ' || p_voyageur_nom || ': ' || p_note
         ELSE '[Site web] Commande de ' || p_voyageur_nom END)
  RETURNING id INTO v_cmd_id;

  RETURN jsonb_build_object(
    'ok', true,
    'commande_id', v_cmd_id,
    'statut', v_statut,
    'prestation', v_presta.nom,
    'montant', v_montant,
    'message', CASE WHEN v_statut = 'confirme'
      THEN 'Votre reservation est confirmee !'
      ELSE 'Votre demande a ete envoyee. L equipe DPM vous confirmera sous peu.' END
  );
END;
$$;

GRANT EXECUTE ON FUNCTION public.upsells_commander(uuid, uuid, text, text, text, date, text, int, text) TO anon;

-- 3. Calendrier public pour le site WordPress
CREATE OR REPLACE FUNCTION public.calendar_public(p_bien_id uuid, p_months int DEFAULT 3)
RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER
AS $$
DECLARE
  v_bien record;
  v_today date := CURRENT_DATE;
  v_end date;
  v_occupied jsonb;
BEGIN
  SELECT id, nom, nuits_min INTO v_bien
  FROM bien WHERE id = p_bien_id;
  IF NOT FOUND THEN
    RETURN jsonb_build_object('error', 'Bien introuvable');
  END IF;

  v_end := v_today + (COALESCE(p_months, 3) * interval '1 month');

  SELECT COALESCE(jsonb_agg(
    jsonb_build_object('start', r.arrivee, 'end', r.depart)
  ), '[]'::jsonb) INTO v_occupied
  FROM reservation r
  WHERE r.bien_id = p_bien_id
    AND r.statut IN ('confirmee', 'en_attente', 'demande')
    AND r.depart >= v_today
    AND r.arrivee <= v_end;

  RETURN jsonb_build_object(
    'bien_id', p_bien_id,
    'nom', COALESCE(v_bien.nom, ''),
    'nuits_min', COALESCE(v_bien.nuits_min, 1),
    'occupied', v_occupied,
    'generated_at', now()
  );
END;
$$;

GRANT EXECUTE ON FUNCTION public.calendar_public(uuid, int) TO anon;
