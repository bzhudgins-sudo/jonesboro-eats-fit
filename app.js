'use strict';
const $=s=>document.querySelector(s),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ALLERGENS=[['dairy','Dairy'],['egg','Egg'],['gluten','Gluten/wheat'],['soy','Soy'],['peanut','Peanut'],['treenut','Tree nuts'],['fish','Fish'],['shellfish','Shellfish'],['sesame','Sesame'],['tomato','Tomato'],['fruit','Fresh fruit (incl. avocado)'],['carrot','Carrot']];
const DEFAULT={goal:'maintain',sex:'',age:'',heightIn:'',weightLb:'',activity:'1.375',calTarget:2200,protein:150,allergies:['tomato','fruit','carrot'],dislikes:''};
let P=load('ef_profile',DEFAULT),D={},view='list';
function load(k,d){try{return Object.assign(structuredClone(d),JSON.parse(localStorage.getItem(k))||{})}catch(e){return structuredClone(d)}}
function save(k,v){localStorage.setItem(k,JSON.stringify(v))}
// "Likely" allergen tags inferred from dish names (tomato, fresh fruit, carrot + a few common ones)
const LIKELY=[['tomato',/tomato|burger|pounder|mcdouble|mcchicken|whopper|sandwich|salsa|pico|ketchup|marinara|pizza|bbq|barbe|chili\b|enchilada|ranchero|rotel|cocktail sauce|whopper|big mac|blt|club|deluxe|sloppy|spaghetti|lasagna|bloody|taco|burrito|nacho|sub\b|hoagie|italian|meatball/i],
 ['fruit',/avocado|guac|berr|apple|fruit|smoothie|banana|lemon|orange|peach|mango|pineapple|cranberr|cherr|grape|coconut|parfait|acai/i],
 ['carrot',/carrot|salad|slaw|lo mein|egg roll|pot pie|soup|stir fry|fried rice|veggie|vegetable/i]];
function tagsFor(it){const s=new Set(it.allergens||[]);for(const[t,re]of LIKELY)if(re.test(it.name))s.add(t);return{tags:[...s],unknown:it.allergens==null}}
function targets(){let cal=+P.calTarget||2200;const a=+P.age,h=+P.heightIn,w=+P.weightLb;
 if(a&&h&&w&&P.sex){const kg=w/2.2046,cm=h*2.54;const bmr=10*kg+6.25*cm-5*a+(P.sex==='m'?5:-161);cal=Math.round(bmr*(+P.activity||1.375)*({cut:.8,maintain:1,bulk:1.12}[P.goal]))}
 return{cal,protein:+P.protein||Math.round((w||180)*0.8),meal:Math.round(cal/3),mealP:Math.round((+P.protein||150)/3)}}
function score(it,snack){const T=targets();const tgt=snack?Math.round(T.cal*.12):T.meal,tp=snack?Math.round(T.protein*.12):T.mealP;
 const cal=it.cal||1,dens=Math.min(1,(it.protein*4/cal)/0.4),near=Math.max(0,1-Math.abs(cal-tgt)/tgt),pAbs=Math.min(1,it.protein/tp);
 const w={cut:[.30,.50,.20],maintain:[.40,.35,.25],bulk:[.45,.20,.35]}[P.goal]||[.4,.35,.25];
 let s=100*(w[0]*near+w[1]*dens+w[2]*pAbs);if(P.goal==='cut'&&cal>tgt*1.3)s-=10;return Math.max(0,Math.round(s))}
function filt(items,snack){const hp=$('#fHP').checked,mx=+$('#fMax').value||0,showAl=$('#fShowAl').checked,q=$('#q').value.trim().toLowerCase();
 const dis=P.dislikes.split(',').map(s=>s.trim().toLowerCase()).filter(Boolean);const out=[];
 for(const it of items){if(it.cal==null||it.protein==null)continue;if(hp&&it.protein<(snack?15:30))continue;if(mx&&it.cal>mx)continue;
  if(dis.some(d=>it.name.toLowerCase().includes(d)))continue;
  const{tags,unknown}=tagsFor(it);const hit=tags.filter(t=>P.allergies.includes(t));if(hit.length&&!showAl)continue;
  out.push({...it,hit,unknown,score:score(it,snack)})}
 return out.sort((a,b)=>b.score-a.score)}
const AN=Object.fromEntries(ALLERGENS);
function itemHTML(it,label){return `<div class="item"><div class="r"><div><b>${esc(it.name)}</b> <span class="pill ${label==='Official'?'off':'est'}">${label}</span>
 <div class="macros">${it.cal} cal · <b>${it.protein} g protein</b> · ${it.carbs??'–'} g carbs · ${it.fat??'–'} g fat${it.serving?' · '+esc(it.serving):''}${it.portion?' · '+esc(it.portion):''}</div>
 ${it.hit.length?`<div class="warn">⚠ May contain your allergens: ${it.hit.map(t=>AN[t]).join(', ')}</div>`:''}
 ${it.unknown&&P.allergies.length?'<div class="warn" style="background:#2a2410;color:#fde68a">Allergens not listed — verify</div>':''}</div><div class="score" title="Fit score">${it.score}</div></div></div>`}
function dataFor(r){const n=(r.brand||r.name||'').toLowerCase();
 for(const[k,c]of Object.entries(D.nut.chains))if(c.match.some(m=>n===m||n.startsWith(m)))return{label:'Official',src:c.source,date:c.retrieved,note:c.note,items:c.items,cname:c.name};
 for(const[k,c]of Object.entries(D.loc.restaurants))if(c.match.some(m=>n.includes(m)))return{label:'Estimated',src:c.menu_source,note:D.loc.method,items:c.items,cname:c.name};
 return null}
function renderList(){const q=$('#q').value.trim().toLowerCase(),only=$('#fData').checked;const rows=[];
 for(const r of D.rest){const d=dataFor(r);if(only&&!d)continue;const nm=r.name||r.brand||'Unnamed';
  let best=null,cnt=0;if(d){const f=filt(d.items);cnt=f.length;best=f[0];if(q&&!nm.toLowerCase().includes(q)&&!f.some(i=>i.name.toLowerCase().includes(q)))continue}else if(q&&!nm.toLowerCase().includes(q))continue;
  rows.push({r,d,nm,best,cnt})}
 rows.sort((a,b)=>(b.best?.score??-1)-(a.best?.score??-1));
 $('#v-list').innerHTML=`<div class="sub" style="padding:0 14px">${rows.length} places · per-meal target ≈ ${targets().meal} cal / ${targets().mealP} g protein</div>`+rows.map(x=>`<div class="card place" data-id="${esc(x.r.id)}"><div class="r"><div><h3>${esc(x.nm)}</h3><div class="sub">${esc(x.r.addr||x.r.cuisine||x.r.amenity)}</div>
 ${x.d?(x.best?`<div class="sub">Top pick: <b>${esc(x.best.name)}</b> — ${x.best.cal} cal, ${x.best.protein} g P</div>`:'<div class="sub">No items match your filters</div>'):'<div class="sub">No nutrition data yet</div>'}</div>
 ${x.d?`<span class="pill ${x.d.label==='Official'?'off':'est'}">${x.d.label}</span>`:''}</div></div>`).join('');
 document.querySelectorAll('.place').forEach(e=>e.onclick=()=>detail(e.dataset.id))}
function detail(id){const r=D.rest.find(x=>x.id===id),d=dataFor(r);show('detail');const notes=load('ef_suggest',{});
 let h=`<div class="card"><button class="btn" id="back">← Back</button><h2>${esc(r.name||r.brand)}</h2><div class="sub">${esc(r.addr||'')}${r.website?` · <a href="${esc(r.website)}" target="_blank" rel="noopener">website</a>`:''}</div>`;
 if(d){const f=filt(d.items);h+=`<p class="sub"><span class="pill ${d.label==='Official'?'off':'est'}">${d.label}</span> Source: ${/^https?:/.test(d.src)?`<a href="${esc(d.src.split(' ')[0])}" target="_blank" rel="noopener">${esc(d.src)}</a>`:esc(d.src)}${d.date?' · retrieved '+d.date:''}${d.note?'<br>'+esc(d.note):''}</p><h3>What to order (ranked for your goal)</h3>`+(f.length?f.map(i=>itemHTML(i,d.label)).join(''):'<p class="sub">No items match your filters/allergies.</p>')}
 else h+=`<p><b>No nutrition data yet.</b></p>`;
 h+=`<h3>Suggest a menu item</h3><textarea id="sug" rows="3" placeholder="e.g. Grilled chicken plate">${esc(notes[id]||'')}</textarea><button class="btn pri" id="sugSave" style="margin-top:6px">Save note (on this phone)</button> <span id="sugOk" class="sub"></span></div>`;
 $('#v-detail').innerHTML=h;$('#back').onclick=()=>show('list');$('#sugSave').onclick=()=>{const n=load('ef_suggest',{});n[id]=$('#sug').value;save('ef_suggest',n);$('#sugOk').textContent='Saved'};scrollTo(0,0)}
function renderSnacks(){const f=filt(D.kr.items,true);$('#v-snacks').innerHTML=`<div class="card"><h2>Kroger grab-and-go snacks</h2><p class="sub">${esc(D.kr.note)}</p>`+(f.length?f.map(i=>itemHTML(i,'Official').replace('</b> <span',`</b> <span class="sub">${esc(i.brand)}</span> <a class="sub" href="${esc(i.source)}" target="_blank" rel="noopener">FDC</a> <span`)).join(''):'<p class="sub">No snacks match.</p>')+'</div>'}
function renderProfile(){const T=targets();$('#v-profile').innerHTML=`<div class="card"><h2>Your profile</h2><p class="sub">Saved only on this device.</p>
 <label>Goal<select id="pGoal">${['cut','maintain','bulk'].map(g=>`<option ${P.goal===g?'selected':''}>${g}</option>`).join('')}</select></label>
 <h3>Body metrics (optional → calorie target)</h3><div class="row"><label>Sex<select id="pSex"><option value="">–</option><option value="m" ${P.sex==='m'?'selected':''}>male</option><option value="f" ${P.sex==='f'?'selected':''}>female</option></select></label>
 <label>Age<input id="pAge" type="number" value="${esc(P.age)}"></label><label>Height (in)<input id="pH" type="number" value="${esc(P.heightIn)}"></label><label>Weight (lb)<input id="pW" type="number" value="${esc(P.weightLb)}"></label>
 <label>Activity<select id="pAct">${[['1.2','Sedentary'],['1.375','Light'],['1.55','Moderate'],['1.725','Very active']].map(([v,n])=>`<option value="${v}" ${P.activity===v?'selected':''}>${n}</option>`).join('')}</select></label></div>
 <div class="row"><label>Daily calories (used if no metrics)<input id="pCal" type="number" value="${esc(P.calTarget)}"></label><label>Protein target (g/day)<input id="pP" type="number" value="${esc(P.protein)}"></label></div>
 <h3>Allergies</h3><div class="chips">${ALLERGENS.map(([k,n])=>`<label><input type="checkbox" class="pAl" value="${k}" ${P.allergies.includes(k)?'checked':''}> ${n}</label>`).join('')}</div>
 <h3>Dislikes</h3><input id="pDis" type="text" placeholder="comma separated, e.g. mushroom, onion" value="${esc(P.dislikes)}">
 <p><button class="btn pri" id="pSave">Save profile</button> <span id="pOk" class="sub"></span></p><p class="sub" id="pT">Daily target: ${T.cal} cal, ${T.protein} g protein (≈${T.meal} cal / ${T.mealP} g per meal)</p></div>`;
 $('#pSave').onclick=()=>{P={goal:$('#pGoal').value,sex:$('#pSex').value,age:$('#pAge').value,heightIn:$('#pH').value,weightLb:$('#pW').value,activity:$('#pAct').value,calTarget:$('#pCal').value,protein:$('#pP').value,allergies:[...document.querySelectorAll('.pAl:checked')].map(e=>e.value),dislikes:$('#pDis').value};save('ef_profile',P);$('#pOk').textContent='Saved ✓';const T=targets();$('#pT').textContent=`Daily target: ${T.cal} cal, ${T.protein} g protein (≈${T.meal} cal / ${T.mealP} g per meal)`}}
let map;function renderMap(){if(map){map.invalidateSize();return}map=L.map('map').setView([35.83,-90.69],12);
 L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
 for(const r of D.rest){const d=dataFor(r);L.circleMarker([r.lat,r.lon],{radius:7,color:d?(d.label==='Official'?'#22c55e':'#f59e0b'):'#64748b',fillOpacity:.8}).addTo(map).bindPopup(`<b>${esc(r.name||r.brand)}</b><br>${d?d.label+' data':'No nutrition data yet'}<br><a href="#" onclick="detail('${esc(r.id)}');return false">Details</a>`)}}
function show(v){view=v;document.querySelectorAll('.view').forEach(e=>e.classList.add('hidden'));$('#v-'+v).classList.remove('hidden');
 document.querySelectorAll('#tabs button').forEach(b=>b.classList.toggle('on',b.dataset.v===v));$('#filters').classList.toggle('hidden',v==='profile'||v==='map');
 if(v==='list')renderList();if(v==='map')renderMap();if(v==='snacks')renderSnacks();if(v==='profile')renderProfile()}
function net(){$('#net').textContent=navigator.onLine?'online':'offline'}
(async()=>{const g=u=>fetch(u).then(r=>r.json());const[rs,nut,loc,kr]=await Promise.all(['data/restaurants.json','data/nutrition.json','data/local-estimates.json','data/kroger-snacks.json'].map(g));
 D={rest:rs.restaurants,nut,loc,kr};document.querySelectorAll('#tabs button').forEach(b=>b.onclick=()=>show(b.dataset.v));
 ['#q','#fHP','#fMax','#fData','#fShowAl'].forEach(s=>$(s).addEventListener('input',()=>show(view==='detail'?'list':view)));
 addEventListener('online',net);addEventListener('offline',net);net();show('list');
 if('serviceWorker'in navigator)navigator.serviceWorker.register('sw.js')})();
