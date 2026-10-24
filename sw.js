const V='eatsfit-v2';const CORE=['./','index.html','app.css','app.js','manifest.webmanifest','vendor/leaflet.js','vendor/leaflet.css','vendor/images/marker-icon.png','vendor/images/marker-icon-2x.png','vendor/images/marker-shadow.png','icons/apple-touch-icon.png','icons/icon-192.png','data/restaurants.json','data/nutrition.json','data/local-estimates.json','data/kroger-snacks.json'];
self.addEventListener('install',e=>e.waitUntil(caches.open(V).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==V).map(x=>caches.delete(x)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET')return;
 if(u.hostname.endsWith('tile.openstreetmap.org')){e.respondWith(caches.open(V+'-tiles').then(c=>c.match(e.request).then(r=>r||fetch(e.request).then(n=>{c.put(e.request,n.clone());return n}).catch(()=>new Response('',{status:504})))));return}
 if(u.origin!==location.origin)return;
 e.respondWith(fetch(e.request).then(n=>{const cp=n.clone();caches.open(V).then(c=>c.put(e.request,cp));return n}).catch(()=>caches.match(e.request,{ignoreSearch:true}).then(r=>r||caches.match('index.html'))))});
