import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'content-type',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
};

/**
 * Edge Function : catalogue public des prestations (upsells) pour un bien donné.
 * Utilisée par le site WordPress dpmconciergerie-group.com.
 *
 * GET /upsells-public?bien_id=xxx[&lang=fr]
 *
 * Retourne uniquement les prestations marquées « visible_site = true »
 * dans la table bien_prestation, ou toutes les prestations actives si
 * aucune sélection personnalisée n'existe pour ce bien.
 * Les prestations « séjour uniquement » (visible_site=false) ne sont
 * jamais exposées sur le site public.
 */
Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const url = new URL(req.url);
    const bienId = url.searchParams.get('bien_id');

    if (!bienId) {
      return new Response(JSON.stringify({ error: 'bien_id requis' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    );

    // 1. Charger le bien (nom, propriétaire)
    const { data: bien } = await supabase
      .from('bien')
      .select('id, nom, proprietaire_id')
      .eq('id', bienId)
      .maybeSingle();

    if (!bien) {
      return new Response(JSON.stringify({ error: 'Bien introuvable' }), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // 2. Charger les liens bien_prestation (sélection personnalisée)
    const { data: liens } = await supabase
      .from('bien_prestation')
      .select('prestation_id, visible_site')
      .eq('bien_id', bienId);

    const hasCustomSelection = liens && liens.length > 0;
    const visibleOnSite = new Set(
      (liens || []).filter(l => l.visible_site).map(l => l.prestation_id)
    );
    const selectedIds = new Set(
      (liens || []).map(l => l.prestation_id)
    );

    // 3. Charger toutes les prestations actives
    const { data: prestations } = await supabase
      .from('prestation')
      .select('id, nom, categorie, type, icone, unite, description, prix_logement, prix_exterieur, prix_public_logement, prix_public_exterieur, au_logement, a_l_exterieur, partenaire_id, proprietaire_id, horaires, visible_site')
      .eq('actif', true)
      .order('categorie')
      .order('nom');

    // 4. Filtrer : ne garder que celles visibles sur le site pour ce bien
    const filtered = (prestations || []).filter(p => {
      // Prestations internes : seulement celles du propriétaire du bien
      if (p.type === 'interne' && p.proprietaire_id !== bien.proprietaire_id) return false;

      if (hasCustomSelection) {
        // Sélection personnalisée : la prestation doit être dans la liste ET visible_site
        return visibleOnSite.has(p.id);
      } else {
        // Pas de sélection : la prestation elle-même doit être marquée visible_site
        return p.visible_site === true || p.visible_site === 'true';
      }
    });

    // 5. Grouper par catégorie
    const categories: Record<string, any[]> = {};
    for (const p of filtered) {
      const cat = p.categorie || 'Autres';
      if (!categories[cat]) categories[cat] = [];
      categories[cat].push({
        id: p.id,
        nom: p.nom,
        icone: p.icone || '',
        unite: p.unite || '',
        description: p.description || '',
        au_logement: p.au_logement,
        a_l_exterieur: p.a_l_exterieur,
        prix_logement: p.au_logement ? (p.prix_public_logement || p.prix_logement || 0) : null,
        prix_exterieur: p.a_l_exterieur ? (p.prix_public_exterieur || p.prix_exterieur || 0) : null,
        horaires: p.horaires || null,
      });
    }

    // 6. Charger les noms des partenaires (pour affichage sur le site)
    const partIds = [...new Set(filtered.filter(p => p.type === 'externe' && p.partenaire_id).map(p => p.partenaire_id))];
    let partenaires: Record<string, string> = {};
    if (partIds.length) {
      const { data: parts } = await supabase
        .from('partenaire')
        .select('id, nom')
        .in('id', partIds);
      for (const pa of (parts || [])) partenaires[pa.id] = pa.nom;
    }

    return new Response(JSON.stringify({
      bien_id: bienId,
      bien_nom: bien.nom,
      total: filtered.length,
      categories,
      partenaires,
      generated_at: new Date().toISOString()
    }), {
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=300' // 5 min cache
      }
    });

  } catch (err) {
    return new Response(JSON.stringify({ error: 'Erreur serveur' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
});
