const V='eatsfit-v13';const CORE=['./','index.html','app.css','app.js','manifest.webmanifest','icons/apple-touch-icon.png','icons/icon-192.png','data/restaurants.json','data/nutrition.json','data/local-estimates.json','data/kroger-snacks.json'];
self.addEventListener('install',e=>e.waitUntil(caches.open(V).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==V).map(x=>caches.delete(x)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET')return;
 if(u.origin!==location.origin)return;
 e.respondWith(fetch(e.request).then(n=>{const cp=n.clone();caches.open(V).then(c=>c.put(e.request,cp));return n}).catch(()=>caches.match(e.request,{ignoreSearch:true}).then(r=>r||caches.match('index.html'))))});
