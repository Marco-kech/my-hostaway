import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

/**
 * Edge Function : recevoir une commande d'upsell depuis le site WordPress.
 * Le site envoie un POST avec les infos de la commande, et cette fonction
 * crée la commande dans My Hostaway (table « commande ») au statut « attente ».
 *
 * POST /upsells-order
 * Body JSON :
 * {
 *   bien_id: "...",
 *   prestation_id: "...",
 *   reservation_id?: "..." (optionnel, si le voyageur est déjà en séjour),
 *   voyageur_nom: "Jean Dupont",
 *   voyageur_email: "jean@example.com",
 *   voyageur_tel?: "...",
 *   date: "2026-12-15",
 *   heure?: "14:00",
 *   quantite: 2,
 *   note?: "Commentaire du voyageur",
 *   source: "site_web"
 * }
 *
 * Retourne { ok: true, commande_id: "..." }
 */
Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'POST requis' }), {
      status: 405,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }

  try {
    const body = await req.json();
    const { bien_id, prestation_id, reservation_id, voyageur_nom, voyageur_email, voyageur_tel, date, heure, quantite, note } = body;

    // Validation
    if (!bien_id || !prestation_id || !date || !voyageur_nom) {
      return new Response(JSON.stringify({
        error: 'Champs requis : bien_id, prestation_id, date, voyageur_nom'
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    );

    // 1. Vérifier que le bien existe et récupérer le tenant_id
    const { data: bien } = await supabase
      .from('bien')
      .select('id, tenant_id, nom')
      .eq('id', bien_id)
      .maybeSingle();

    if (!bien) {
      return new Response(JSON.stringify({ error: 'Bien introuvable' }), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // 2. Vérifier que la prestation existe et est active
    const { data: presta } = await supabase
      .from('prestation')
      .select('id, nom, type, prix_logement, prix_exterieur, net_partenaire, partenaire_id, proprietaire_id, commission_logement, mode_commission_logement, validation')
      .eq('id', prestation_id)
      .eq('actif', true)
      .maybeSingle();

    if (!presta) {
      return new Response(JSON.stringify({ error: 'Prestation introuvable ou inactive' }), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // 3. Chercher ou créer le voyageur par email
    let voyageur_id: string | null = null;
    if (voyageur_email) {
      const { data: existing } = await supabase
        .from('voyageur')
        .select('id')
        .eq('tenant_id', bien.tenant_id)
        .eq('email', voyageur_email)
        .maybeSingle();

      if (existing) {
        voyageur_id = existing.id;
      } else {
        const { data: newVoy } = await supabase
          .from('voyageur')
          .insert({
            tenant_id: bien.tenant_id,
            nom: voyageur_nom,
            email: voyageur_email,
            tel: voyageur_tel || null,
            source: 'site_web'
          })
          .select('id')
          .single();
        if (newVoy) voyageur_id = newVoy.id;
      }
    }

    // 4. Calculer les montants
    const qty = Math.max(1, parseInt(String(quantite)) || 1);
    const prix_unitaire = presta.prix_logement || presta.prix_exterieur || 0;
    const montant = prix_unitaire * qty;

    // Calcul commission
    let part_conciergerie = 0;
    let reversement = presta.net_partenaire ? presta.net_partenaire * qty : 0;
    let part_proprietaire = 0;

    if (presta.type === 'externe') {
      // Partenaire : montant - net_partenaire = marge DPM
      part_conciergerie = montant - reversement;
    } else if (presta.type === 'interne') {
      // Interne propriétaire : commission en % ou montant
      const commVal = presta.commission_logement || 0;
      if (presta.mode_commission_logement === 'pct') {
        part_conciergerie = Math.round(montant * commVal / 100);
      } else {
        part_conciergerie = commVal * qty;
      }
      part_proprietaire = montant - part_conciergerie;
    } else {
      // DPM : tout pour la conciergerie
      part_conciergerie = montant;
    }

    // 5. Créer la commande
    const statut = presta.validation === 'auto' ? 'confirme' : 'attente';

    const { data: commande, error } = await supabase
      .from('commande')
      .insert({
        tenant_id: bien.tenant_id,
        bien_id,
        prestation_id,
        reservation_id: reservation_id || null,
        voyageur_id,
        date,
        heure: heure || null,
        quantite: qty,
        montant,
        part_conciergerie,
        reversement,
        part_proprietaire,
        statut,
        reglement: 'non',
        source: 'site_web',
        note: note ? `[Site web] ${voyageur_nom}: ${note}` : `[Site web] Commande de ${voyageur_nom}`
      })
      .select('id')
      .single();

    if (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    return new Response(JSON.stringify({
      ok: true,
      commande_id: commande.id,
      statut,
      prestation: presta.nom,
      montant,
      message: statut === 'confirme'
        ? 'Votre réservation est confirmée ! Vous recevrez un e-mail de confirmation.'
        : 'Votre demande a été envoyée. L\'équipe DPM Conciergerie vous confirmera sous peu.'
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });

  } catch (err) {
    return new Response(JSON.stringify({ error: 'Erreur serveur' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
});
