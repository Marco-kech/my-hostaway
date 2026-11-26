/**
 * DPM Conciergerie — Widget Catalogue d'Upsells
 * À intégrer sur WordPress via un bloc HTML personnalisé.
 *
 * Usage :
 *   <div id="dpm-upsells" data-bien-id="ID_DU_BIEN"></div>
 *   <script src="https://marco-kech.github.io/my-hostaway/widget-upsells.js"></script>
 *
 * Options (data-attributes) :
 *   data-bien-id    : ID du bien Supabase (obligatoire)
 *   data-theme      : "light" (défaut) ou "dark"
 *   data-lang       : "fr" (défaut), "en", "es", "de", "ar", "nl"
 */
(function () {
  'use strict';

  const SUPABASE_URL = 'https://eztwwzzjzwmhfzmcafyu.supabase.co';
  const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6dHd3enpqendtaGZ6bWNhZnl1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzIzNjQ4MDYsImV4cCI6MjA0Nzk0MDgwNn0.sb_publishable_v8lL0wuTAC7uHpuNuzE8WQ_O8vIOgg4';
  const RPC_URL = SUPABASE_URL + '/rest/v1/rpc/';

  const C = {
    vert: '#14352A',
    or: '#C9A227',
    creme: '#FBFAF6',
    blanc: '#ffffff',
    gris: '#f5f5f5',
    text: '#333333',
    muted: '#888888'
  };

  const LABELS = {
    fr: { title: 'Nos prestations', surPlace: 'Sur place', exterieur: 'À l\'extérieur', from: 'À partir de', perPerson: '/ pers.', perHour: '/ heure', flat: 'forfait', book: 'Réserver', close: 'Fermer', name: 'Votre nom', email: 'Votre e-mail', phone: 'Téléphone', date: 'Date souhaitée', time: 'Heure', qty: 'Nombre de personnes', note: 'Commentaire', send: 'Envoyer la demande', sending: 'Envoi…', success: 'Demande envoyée !', error: 'Erreur, veuillez réessayer.', noPresta: 'Aucune prestation disponible pour le moment.', loading: 'Chargement…' },
    en: { title: 'Our services', surPlace: 'On-site', exterieur: 'Off-site', from: 'From', perPerson: '/ person', perHour: '/ hour', flat: 'flat rate', book: 'Book', close: 'Close', name: 'Your name', email: 'Your email', phone: 'Phone', date: 'Preferred date', time: 'Time', qty: 'Number of people', note: 'Comment', send: 'Send request', sending: 'Sending…', success: 'Request sent!', error: 'Error, please try again.', noPresta: 'No services available at the moment.', loading: 'Loading…' }
  };

  const container = document.getElementById('dpm-upsells');
  if (!container) return;

  const bienId = container.dataset.bienId;
  const lang = container.dataset.lang || 'fr';
  const L = LABELS[lang] || LABELS.fr;

  if (!bienId) { container.innerHTML = '<p style="color:red">Erreur : data-bien-id manquant</p>'; return; }

  // Inject CSS
  const style = document.createElement('style');
  style.textContent = `
    .dpm-ups { font-family: Arial, 'Helvetica Neue', sans-serif; max-width: 700px; margin: 0 auto; }
    .dpm-ups-header { background: ${C.vert}; color: ${C.blanc}; padding: 16px 20px; border-radius: 12px 12px 0 0; }
    .dpm-ups-header h3 { margin: 0; font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.3em; }
    .dpm-ups-tabs { display: flex; border-bottom: 2px solid ${C.or}; background: ${C.creme}; }
    .dpm-ups-tab { flex: 1; padding: 10px; text-align: center; cursor: pointer; font-weight: 600; font-size: 0.9em; color: ${C.muted}; border-bottom: 3px solid transparent; transition: all 0.2s; }
    .dpm-ups-tab.active { color: ${C.vert}; border-bottom-color: ${C.or}; }
    .dpm-ups-body { background: ${C.blanc}; border: 1px solid #e0e0e0; border-top: 0; border-radius: 0 0 12px 12px; padding: 16px; max-height: 500px; overflow-y: auto; }
    .dpm-ups-cat { font-weight: 700; font-size: 0.95em; color: ${C.vert}; margin: 16px 0 8px; padding-bottom: 4px; border-bottom: 1px solid #eee; }
    .dpm-ups-cat:first-child { margin-top: 0; }
    .dpm-ups-card { display: flex; align-items: center; padding: 10px; border-radius: 8px; margin-bottom: 6px; background: ${C.gris}; transition: box-shadow 0.2s; }
    .dpm-ups-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
    .dpm-ups-icon { font-size: 1.5em; margin-right: 12px; min-width: 32px; text-align: center; }
    .dpm-ups-info { flex: 1; }
    .dpm-ups-name { font-weight: 600; font-size: 0.95em; }
    .dpm-ups-desc { font-size: 0.8em; color: ${C.muted}; margin-top: 2px; }
    .dpm-ups-price { font-weight: 700; color: ${C.or}; font-size: 1em; margin-right: 10px; white-space: nowrap; }
    .dpm-ups-btn { background: ${C.or}; color: ${C.vert}; border: none; padding: 7px 14px; border-radius: 6px; font-weight: 600; font-size: 0.85em; cursor: pointer; transition: background 0.2s; }
    .dpm-ups-btn:hover { background: #b8911f; }
    .dpm-ups-modal { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 10000; }
    .dpm-ups-form { background: ${C.blanc}; border-radius: 12px; padding: 24px; max-width: 400px; width: 90%; box-shadow: 0 8px 32px rgba(0,0,0,0.2); }
    .dpm-ups-form h4 { margin: 0 0 16px; color: ${C.vert}; font-family: 'Cormorant Garamond', Georgia, serif; }
    .dpm-ups-form label { display: block; font-size: 0.8em; font-weight: 600; color: ${C.muted}; margin-bottom: 3px; margin-top: 10px; }
    .dpm-ups-form input, .dpm-ups-form textarea { width: 100%; padding: 8px 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.9em; box-sizing: border-box; }
    .dpm-ups-form textarea { height: 60px; resize: vertical; }
    .dpm-ups-form .dpm-ups-actions { display: flex; gap: 8px; margin-top: 16px; }
    .dpm-ups-form .dpm-ups-actions button { flex: 1; padding: 10px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; font-size: 0.9em; }
    .dpm-ups-submit { background: ${C.or}; color: ${C.vert}; }
    .dpm-ups-cancel { background: #eee; color: #555; }
    .dpm-ups-msg { padding: 10px; border-radius: 6px; margin-top: 10px; font-size: 0.9em; text-align: center; }
    .dpm-ups-empty { text-align: center; padding: 40px 20px; color: ${C.muted}; }
  `;
  document.head.appendChild(style);

  container.innerHTML = `<div class="dpm-ups"><div class="dpm-ups-header"><h3>${L.title}</h3></div><div class="dpm-ups-body"><div class="dpm-ups-empty">${L.loading}</div></div></div>`;

  // Fetch data via Supabase RPC
  fetch(RPC_URL + 'upsells_catalogue', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY },
    body: JSON.stringify({ p_bien_id: bienId })
  })
    .then(r => r.json())
    .then(data => {
      if (data.error) { container.querySelector('.dpm-ups-body').innerHTML = `<div class="dpm-ups-empty">${data.error}</div>`; return; }
      // Adapt RPC response: prestations flat array → categories grouped
      if (data.prestations && !data.categories) {
        const cats = {};
        (data.prestations || []).forEach(p => { const c = p.categorie || 'Autres'; if (!cats[c]) cats[c] = []; cats[c].push(p); });
        data.categories = cats;
      }
      render(data);
    })
    .catch(() => {
      container.querySelector('.dpm-ups-body').innerHTML = `<div class="dpm-ups-empty">${L.error}</div>`;
    });

  function render(data) {
    const cats = data.categories || {};
    const allPrestas = Object.values(cats).flat();
    if (!allPrestas.length) {
      container.querySelector('.dpm-ups-body').innerHTML = `<div class="dpm-ups-empty">${L.noPresta}</div>`;
      return;
    }

    // Split sur place / extérieur
    const surPlace = allPrestas.filter(p => p.au_logement);
    const exterieur = allPrestas.filter(p => p.a_l_exterieur);
    const hasBoth = surPlace.length > 0 && exterieur.length > 0;

    let tabsHtml = '';
    if (hasBoth) {
      tabsHtml = `<div class="dpm-ups-tabs">
        <div class="dpm-ups-tab active" data-tab="surplace">${L.surPlace}</div>
        <div class="dpm-ups-tab" data-tab="exterieur">${L.exterieur}</div>
      </div>`;
    }

    const renderList = (prestas, priceKey) => {
      const byCat = {};
      prestas.forEach(p => { const cat = findCat(cats, p.id); if (!byCat[cat]) byCat[cat] = []; byCat[cat].push(p); });
      return Object.entries(byCat).map(([cat, items]) =>
        `<div class="dpm-ups-cat">${escH(cat)}</div>` +
        items.map(p => {
          const prix = priceKey === 'logement' ? p.prix_logement : p.prix_exterieur;
          const unite = p.unite || '';
          return `<div class="dpm-ups-card">
            <div class="dpm-ups-icon">${p.icone || '✨'}</div>
            <div class="dpm-ups-info">
              <div class="dpm-ups-name">${escH(p.nom)}</div>
              ${p.description ? `<div class="dpm-ups-desc">${escH(p.description.slice(0, 80))}</div>` : ''}
            </div>
            <div class="dpm-ups-price">${prix ? formatPrice(prix) + (unite ? ' ' + escH(unite) : '') : ''}</div>
            <button class="dpm-ups-btn" data-pid="${p.id}" data-pnom="${escA(p.nom)}" data-prix="${prix || 0}">${L.book}</button>
          </div>`;
        }).join('')
      ).join('');
    };

    const wrapper = container.querySelector('.dpm-ups');
    const header = wrapper.querySelector('.dpm-ups-header').outerHTML;
    wrapper.innerHTML = header + tabsHtml +
      `<div class="dpm-ups-body">
        <div class="dpm-ups-panel" data-panel="surplace">${renderList(surPlace.length ? surPlace : allPrestas, 'logement')}</div>
        ${hasBoth ? `<div class="dpm-ups-panel" data-panel="exterieur" style="display:none">${renderList(exterieur, 'exterieur')}</div>` : ''}
      </div>`;

    // Tab switching
    if (hasBoth) {
      wrapper.querySelectorAll('.dpm-ups-tab').forEach(tab => {
        tab.addEventListener('click', () => {
          wrapper.querySelectorAll('.dpm-ups-tab').forEach(t => t.classList.remove('active'));
          tab.classList.add('active');
          wrapper.querySelectorAll('.dpm-ups-panel').forEach(p => p.style.display = 'none');
          wrapper.querySelector(`[data-panel="${tab.dataset.tab}"]`).style.display = '';
        });
      });
    }

    // Book buttons
    wrapper.querySelectorAll('.dpm-ups-btn').forEach(btn => {
      btn.addEventListener('click', () => openBookForm(btn.dataset.pid, btn.dataset.pnom, btn.dataset.prix));
    });
  }

  function openBookForm(prestaId, prestaName, prix) {
    const overlay = document.createElement('div');
    overlay.className = 'dpm-ups-modal';
    overlay.innerHTML = `<div class="dpm-ups-form">
      <h4>${escH(prestaName)}</h4>
      <label>${L.name} *</label><input id="dpmU_nom" required>
      <label>${L.email} *</label><input id="dpmU_email" type="email" required>
      <label>${L.phone}</label><input id="dpmU_tel">
      <label>${L.date} *</label><input id="dpmU_date" type="date" required>
      <label>${L.time}</label><input id="dpmU_heure" type="time">
      <label>${L.qty}</label><input id="dpmU_qty" type="number" min="1" value="1">
      <label>${L.note}</label><textarea id="dpmU_note"></textarea>
      <div id="dpmU_msg"></div>
      <div class="dpm-ups-actions">
        <button class="dpm-ups-cancel" id="dpmU_cancel">${L.close}</button>
        <button class="dpm-ups-submit" id="dpmU_send">${L.send}</button>
      </div>
    </div>`;
    document.body.appendChild(overlay);

    // Set min date to today
    const dateInput = overlay.querySelector('#dpmU_date');
    dateInput.min = new Date().toISOString().split('T')[0];
    dateInput.value = dateInput.min;

    overlay.querySelector('#dpmU_cancel').addEventListener('click', () => overlay.remove());
    overlay.addEventListener('click', e => { if (e.target === overlay) overlay.remove(); });

    overlay.querySelector('#dpmU_send').addEventListener('click', async () => {
      const nom = overlay.querySelector('#dpmU_nom').value.trim();
      const email = overlay.querySelector('#dpmU_email').value.trim();
      const tel = overlay.querySelector('#dpmU_tel').value.trim();
      const date = overlay.querySelector('#dpmU_date').value;
      const heure = overlay.querySelector('#dpmU_heure').value;
      const qty = parseInt(overlay.querySelector('#dpmU_qty').value) || 1;
      const note = overlay.querySelector('#dpmU_note').value.trim();
      const msgEl = overlay.querySelector('#dpmU_msg');

      if (!nom || !email || !date) {
        msgEl.innerHTML = `<div class="dpm-ups-msg" style="background:#fce4ec;color:#c0392b">Remplissez les champs obligatoires (*)</div>`;
        return;
      }

      const btn = overlay.querySelector('#dpmU_send');
      btn.textContent = L.sending;
      btn.disabled = true;

      try {
        const res = await fetch(RPC_URL + 'upsells_commander', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY },
          body: JSON.stringify({
            p_bien_id: bienId,
            p_prestation_id: prestaId,
            p_voyageur_nom: nom,
            p_voyageur_email: email || null,
            p_voyageur_tel: tel || null,
            p_date: date,
            p_heure: heure || null,
            p_quantite: qty,
            p_note: note || null
          })
        });
        const data = await res.json();
        if (data.ok) {
          msgEl.innerHTML = `<div class="dpm-ups-msg" style="background:#e8f5e9;color:#2e7d32">${L.success}<br><small>${data.message || ''}</small></div>`;
          btn.style.display = 'none';
        } else {
          msgEl.innerHTML = `<div class="dpm-ups-msg" style="background:#fce4ec;color:#c0392b">${data.error || L.error}</div>`;
          btn.textContent = L.send;
          btn.disabled = false;
        }
      } catch (e) {
        msgEl.innerHTML = `<div class="dpm-ups-msg" style="background:#fce4ec;color:#c0392b">${L.error}</div>`;
        btn.textContent = L.send;
        btn.disabled = false;
      }
    });
  }

  // Helpers
  function findCat(cats, id) {
    for (const [cat, items] of Object.entries(cats)) {
      if (items.some(p => p.id === id)) return cat;
    }
    return 'Autres';
  }
  function formatPrice(n) { return new Intl.NumberFormat('fr-MA', { style: 'currency', currency: 'MAD', minimumFractionDigits: 0 }).format(n); }
  function escH(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
  function escA(s) { return s.replace(/"/g, '&quot;').replace(/'/g, '&#39;'); }

})();
