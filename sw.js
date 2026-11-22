const CACHE = 'dpm-hostaway-v3';
const URLS = ['./index.html', './manifest.json', './icon-192.png', './icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(URLS)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);

  // For API calls (Supabase), network only - don't cache
  if (url.hostname.includes('supabase') || url.hostname.includes('anthropic')) return;

  // For app files: network first, fallback to cache (offline support)
  e.respondWith(
    fetch(e.request).then(r => {
      if (r.ok) {
        const clone = r.clone();
        caches.open(CACHE).then(c => c.put(e.request, clone));
      }
      return r;
    }).catch(() => caches.match(e.request).then(r => r || new Response(
      '<html><body style="font-family:Arial;text-align:center;padding:60px;background:#14352A;color:#FBFAF6"><h1>🏠 My Hostaway</h1><p>Vous êtes hors ligne.<br>Vérifiez votre connexion internet.</p></body></html>',
      { headers: { 'Content-Type': 'text/html' } }
    )))
  );
});

// Push notifications support
self.addEventListener('push', e => {
  const data = e.data ? e.data.json() : {};
  const title = data.title || 'My Hostaway';
  const options = {
    body: data.body || 'Nouvelle notification',
    icon: './icon-192.png',
    badge: './icon-192.png',
    tag: data.tag || 'default',
    data: { url: data.url || './' }
  };
  e.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  const url = e.notification.data?.url || './';
  e.waitUntil(clients.openWindow(url));
});
