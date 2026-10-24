// Refresh Jonesboro restaurant list from OpenStreetMap (Overpass). Data © OpenStreetMap contributors, ODbL.
import { writeFileSync } from 'node:fs';
const q = `[out:json][timeout:60];(nwr["amenity"~"^(restaurant|fast_food|cafe)$"](35.76,-90.80,35.92,-90.58););out center tags;`;
const eps = ['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter','https://overpass.private.coffee/api/interpreter'];
let j;
for (const e of eps) { try { const r = await fetch(e,{method:'POST',body:'data='+encodeURIComponent(q),headers:{'Content-Type':'application/x-www-form-urlencoded','User-Agent':'JonesboroEatsFit/1.0'}}); if(r.ok){j=await r.json();break;} console.error(e,r.status);} catch(x){console.error(e,x.message);} }
if(!j) process.exit(1);
const out = j.elements.map(e=>{const t=e.tags||{};return {id:`${e.type}/${e.id}`,name:t.name||t.brand||null,amenity:t.amenity,brand:t.brand||null,brandWikidata:t['brand:wikidata']||null,cuisine:t.cuisine||null,lat:e.lat??e.center?.lat,lon:e.lon??e.center?.lon,addr:[t['addr:housenumber'],t['addr:street']].filter(Boolean).join(' ')||null,website:t.website||null,hours:t.opening_hours||null};}).filter(r=>r.name&&r.lat);
out.sort((a,b)=>a.name.localeCompare(b.name));
writeFileSync(new URL('../data/restaurants.json',import.meta.url),JSON.stringify({generated:new Date().toISOString(),source:'OpenStreetMap via Overpass API',license:'ODbL — © OpenStreetMap contributors',bbox:[35.76,-90.80,35.92,-90.58],restaurants:out},null,1));
console.log('saved',out.length);
