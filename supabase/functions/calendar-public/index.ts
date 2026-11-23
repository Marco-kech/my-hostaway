import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'content-type',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
};

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const url = new URL(req.url);
    const bienId = url.searchParams.get('bien_id');
    const months = parseInt(url.searchParams.get('months') || '3');

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

    const today = new Date().toISOString().split('T')[0];
    const futureDate = new Date();
    futureDate.setMonth(futureDate.getMonth() + months);
    const endDate = futureDate.toISOString().split('T')[0];

    const { data: reservations, error } = await supabase
      .from('reservation')
      .select('arrivee, depart, statut')
      .eq('bien_id', bienId)
      .in('statut', ['confirmee', 'en_attente', 'demande'])
      .gte('depart', today)
      .lte('arrivee', endDate);

    if (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // Only expose date ranges, no guest details
    const occupiedRanges = (reservations || []).map(r => ({
      start: r.arrivee,
      end: r.depart
    }));

    const { data: bien } = await supabase
      .from('bien')
      .select('nom, nuits_min')
      .eq('id', bienId)
      .maybeSingle();

    return new Response(JSON.stringify({
      bien_id: bienId,
      nom: bien?.nom || '',
      nuits_min: bien?.nuits_min || 1,
      occupied: occupiedRanges,
      generated_at: new Date().toISOString()
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=300' }
    });

  } catch (err) {
    return new Response(JSON.stringify({ error: 'Erreur serveur' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
});
