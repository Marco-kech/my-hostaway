/**
 * DPM Conciergerie — Widget Calendrier de Disponibilités
 * À intégrer sur WordPress via un bloc HTML personnalisé.
 *
 * Usage :
 *   <div id="dpm-calendar" data-bien-id="ID_DU_BIEN"></div>
 *   <script src="https://marco-kech.github.io/my-hostaway/widget-calendar.js"></script>
 *
 * Ou en mode direct (sans Edge Function, utilise l'API Supabase directement) :
 *   <div id="dpm-calendar" data-bien-id="ID_DU_BIEN" data-mode="direct"></div>
 */
(function () {
  'use strict';

  // ── Config ──
  const SUPABASE_URL = 'https://eztwwzzjzwmhfzmcafyu.supabase.co';
  const SUPABASE_KEY = 'sb_publishable_v8lL0wuTAC7uHpuNuzE8WQ_O8vIOgg4';
  const EDGE_FN_URL = SUPABASE_URL + '/functions/v1/calendar-public';

  // ── Couleurs DPM ──
  const C = {
    vert: '#14352A',
    or: '#C9A227',
    creme: '#FBFAF6',
    vertClair: '#e8f5e9',
    rougeClair: '#fce4ec',
    gris: '#e0e0e0',
    blanc: '#ffffff'
  };

  const MOIS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
    'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];
  const JOURS = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];

  // ── Inject CSS ──
  const style = document.createElement('style');
  style.textContent = `
    .dpm-cal { font-family: Arial, 'Helvetica Neue', sans-serif; max-width: 420px; margin: 0 auto; background: ${C.blanc}; border-radius: 12px; box-shadow: 0 2px 16px rgba(0,0,0,0.10); overflow: hidden; }
    .dpm-cal-header { background: ${C.vert}; color: ${C.blanc}; display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; }
    .dpm-cal-header h3 { margin: 0; font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.15em; font-weight: 600; }
    .dpm-cal-nav { display: flex; align-items: center; gap: 12px; }
    .dpm-cal-nav button { background: none; border: 1.5px solid rgba(255,255,255,0.4); color: ${C.blanc}; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
    .dpm-cal-nav button:hover { background: rgba(255,255,255,0.15); border-color: ${C.or}; }
    .dpm-cal-month { font-size: 0.95em; min-width: 140px; text-align: center; }
    .dpm-cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; padding: 10px; }
    .dpm-cal-dow { text-align: center; font-size: 0.72em; font-weight: 600; color: #999; padding: 4px 0; text-transform: uppercase; }
    .dpm-cal-day { text-align: center; padding: 8px 2px; border-radius: 8px; font-size: 0.85em; cursor: default; position: relative; transition: all 0.15s; }
    .dpm-cal-day.empty { }
    .dpm-cal-day.available { background: ${C.vertClair}; color: ${C.vert}; font-weight: 500; }
    .dpm-cal-day.occupied { background: ${C.rougeClair}; color: #c0392b; text-decoration: line-through; opacity: 0.7; }
    .dpm-cal-day.past { color: #ccc; background: none; }
    .dpm-cal-day.today { box-shadow: inset 0 0 0 2px ${C.or}; font-weight: 700; }
    .dpm-cal-legend { display: flex; gap: 16px; justify-content: center; padding: 10px 14px 14px; font-size: 0.78em; color: #666; }
    .dpm-cal-legend span { display: flex; align-items: center; gap: 5px; }
    .dpm-cal-legend .dot { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
    .dpm-cal-legend .dot.avail { background: ${C.vertClair}; border: 1px solid #a5d6a7; }
    .dpm-cal-legend .dot.occ { background: ${C.rougeClair}; border: 1px solid #ef9a9a; }
    .dpm-cal-footer { text-align: center; padding: 0 14px 14px; }
    .dpm-cal-footer a { display: inline-block; background: ${C.or}; color: ${C.blanc}; text-decoration: none; padding: 10px 28px; border-radius: 8px; font-weight: 600; font-size: 0.9em; transition: all 0.2s; }
    .dpm-cal-footer a:hover { filter: brightness(1.1); transform: translateY(-1px); }
    .dpm-cal-loading { text-align: center; padding: 40px; color: #999; }
    .dpm-cal-error { text-align: center; padding: 20px; color: #c0392b; font-size: 0.85em; }
    @media (max-width: 480px) { .dpm-cal { max-width: 100%; border-radius: 0; } .dpm-cal-day { padding: 6px 1px; font-size: 0.8em; } }
  `;
  document.head.appendChild(style);

  // ── Helper: check if date is in occupied ranges ──
  function isOccupied(dateStr, ranges) {
    for (const r of ranges) {
      if (dateStr >= r.start && dateStr < r.end) return true;
    }
    return false;
  }

  function dateStr(d) {
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }

  // ── Fetch occupied dates ──
  async function fetchOccupied(bienId, mode) {
    if (mode === 'direct') {
      // Direct Supabase query (no Edge Function needed)
      const today = dateStr(new Date());
      const future = new Date();
      future.setMonth(future.getMonth() + 3);
      const endDate = dateStr(future);

      const url = `${SUPABASE_URL}/rest/v1/reservation?bien_id=eq.${bienId}&statut=in.(confirmee,en_attente,demande)&depart=gte.${today}&arrivee=lte.${endDate}&select=arrivee,depart`;
      const resp = await fetch(url, {
        headers: { 'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY }
      });
      if (!resp.ok) throw new Error('Erreur API');
      const data = await resp.json();
      return {
        occupied: data.map(r => ({ start: r.arrivee, end: r.depart })),
        nom: '',
        nuits_min: 1
      };
    } else {
      // Edge Function mode
      const resp = await fetch(`${EDGE_FN_URL}?bien_id=${bienId}&months=3`);
      if (!resp.ok) throw new Error('Erreur calendrier');
      return await resp.json();
    }
  }

  // ── Render calendar ──
  function renderMonth(container, year, month, occupiedRanges) {
    const today = dateStr(new Date());
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    let startDow = firstDay.getDay(); // 0=Sun
    startDow = startDow === 0 ? 6 : startDow - 1; // Convert to Mon=0

    let html = '';
    // Day of week headers
    for (const j of JOURS) {
      html += `<div class="dpm-cal-dow">${j}</div>`;
    }
    // Empty cells
    for (let i = 0; i < startDow; i++) {
      html += '<div class="dpm-cal-day empty"></div>';
    }
    // Days
    for (let d = 1; d <= lastDay.getDate(); d++) {
      const ds = year + '-' + String(month + 1).padStart(2, '0') + '-' + String(d).padStart(2, '0');
      const isPast = ds < today;
      const isToday = ds === today;
      const occ = isOccupied(ds, occupiedRanges);
      let cls = 'dpm-cal-day';
      if (isPast) cls += ' past';
      else if (occ) cls += ' occupied';
      else cls += ' available';
      if (isToday) cls += ' today';
      html += `<div class="${cls}">${d}</div>`;
    }
    container.innerHTML = html;
  }

  // ── Init Widget ──
  async function init() {
    const el = document.getElementById('dpm-calendar');
    if (!el) return;

    const bienId = el.dataset.bienId;
    const mode = el.dataset.mode || 'direct'; // 'direct' or 'edge'
    const bookingUrl = el.dataset.bookingUrl || '';

    if (!bienId) {
      el.innerHTML = '<div class="dpm-cal-error">Erreur : data-bien-id manquant</div>';
      return;
    }

    el.innerHTML = '<div class="dpm-cal"><div class="dpm-cal-loading">Chargement du calendrier…</div></div>';

    let occupiedRanges = [];
    let nomBien = '';

    try {
      const data = await fetchOccupied(bienId, mode);
      occupiedRanges = data.occupied || [];
      nomBien = data.nom || '';
    } catch (e) {
      el.innerHTML = '<div class="dpm-cal"><div class="dpm-cal-error">Impossible de charger le calendrier</div></div>';
      return;
    }

    // Current display month
    let viewYear = new Date().getFullYear();
    let viewMonth = new Date().getMonth();

    function render() {
      el.innerHTML = `
        <div class="dpm-cal">
          <div class="dpm-cal-header">
            <h3>📅 Disponibilités${nomBien ? ' — ' + nomBien : ''}</h3>
          </div>
          <div class="dpm-cal-nav" style="display:flex;justify-content:center;padding:10px;gap:12px;align-items:center">
            <button id="dpm-prev">◀</button>
            <div class="dpm-cal-month">${MOIS[viewMonth]} ${viewYear}</div>
            <button id="dpm-next">▶</button>
          </div>
          <div class="dpm-cal-grid" id="dpm-grid"></div>
          <div class="dpm-cal-legend">
            <span><span class="dot avail"></span> Disponible</span>
            <span><span class="dot occ"></span> Réservé</span>
          </div>
          ${bookingUrl ? `<div class="dpm-cal-footer"><a href="${bookingUrl}" target="_blank">Réserver maintenant</a></div>` : ''}
        </div>
      `;

      renderMonth(document.getElementById('dpm-grid'), viewYear, viewMonth, occupiedRanges);

      document.getElementById('dpm-prev').onclick = () => {
        viewMonth--;
        if (viewMonth < 0) { viewMonth = 11; viewYear--; }
        render();
      };
      document.getElementById('dpm-next').onclick = () => {
        viewMonth++;
        if (viewMonth > 11) { viewMonth = 0; viewYear++; }
        render();
      };
    }

    render();
  }

  // Auto-init when DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
