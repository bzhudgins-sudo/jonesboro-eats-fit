# Builds data/nutrition.json from official chain data parsed into scripts/raw/ (retrieved 2026-10-24).
import json,re
R='scripts/raw/'
DRINK=re.compile(r"(?i)shake|slush|blast|limeade|soda|\btea\b|coffee|latte|juice|lemonade|pepsi|coke|sprite|dr pepper|water|sauce|dressing|\bdip\b|ketchup|mustard|mayo|add-in|cone|sundae|cake|cookie|\bpie\b|churro|brownie|syrup|cream(er)?\b|smoothie|frapp|float|malt|refresher|drink|chiller|coolatta|macchiato|cappuccino|espresso|donut|munchkin|beer|margarita|wine|cocktail|ritas?\b|iced|frozen|dunkin'|energy|powerade|big red|hi-c|root beer|seasoning|dry rub|spread|jelly|butter$|syrup|packet|topping|cheese sauce|gravy|honey|creamer|crouton|\bbun\b|tortilla|lettuce|tomato$|pickle|onion$|^add |extra |select locations.*(oz)|fl oz|sweetener|fudge|oreo|m&m|reese|candy|chocolate|vanilla|strawberry|caramel")
def keep(o,minc=150):
  if not o['cal'] or not float(o['cal']).is_integer() or o['name'].strip().startswith('-'): return False
  if (o.get('protein') or 0)<4 and not re.search(r'(?i)fries|tots|potato|salad|hash|rings|biscuit|grits|corn|beans|slaw',o['name']): return False
  return o['cal']>=minc and not DRINK.search(o['name'])
def norm(o,al=None):
  d={k:(int(o[k]) if float(o[k]).is_integer() else o[k]) for k in ['cal','protein','carbs','fat','sodium'] if o.get(k) is not None}
  d['name']=re.sub(r'\s+',' ',o['name']).strip(' ,')
  if o.get('cat'): d['cat']=o['cat']
  d['allergens']=o.get('allergens',al)
  return d
def load(f): return json.load(open(R+f))
C={}
def add(key,name,src,items,note=''):
  seen=set();out=[]
  for i in items:
    if i['name'].lower() in seen: continue
    seen.add(i['name'].lower());out.append(i)
  C[key]=dict(name=name,label='Official',source=src,retrieved='2026-10-24',note=note,items=out)
add('chick-fil-a',"Chick-fil-A",'https://www.chick-fil-a.com/nutrition-allergens',[norm(o) for o in load('cfa.out.json') if keep(o,100)],'Allergens not captured; check the official allergen page.')
add('kfc','KFC','https://www.kfc.com/nutrition',[norm(o) for o in load('kfc.out.json') if keep(o,100)])
add('burger-king','Burger King','https://www.bk.com/nutrition-explorer',[norm(o) for o in load('bk.out.json') if o.get('cat') in ('Flame Grilled Burgers','Chicken & Fish','Breakfast','Sides') and keep(o,100)],'Allergen flags include "may contain".')
add('waffle-house','Waffle House','https://www.wafflehouse.com/wp-content/uploads/2026/08/Nutritionals-Allergens-2026-08-27.pdf',[norm(o) for o in load('wh.out.json') if keep(o,60)])
add('mcdonalds',"McDonald's",'https://www.mcdonalds.com/us/en-us/full-menu.html',[norm(o) for o in load('mcd.out.json') if keep(o,100)])
add('sonic','Sonic','https://assets.ctfassets.net/whnlxz6bna9d/665Hn9SdgyT53pJgF9cmkK/090ae5fe05d8cd9643fb98fcde32ef1a/61667-1_FEE_0926_NUTBRO_SEPTEMBER_FA_rg_WCAG.pdf',[norm(o) for o in load('sonic.raw.json') if keep(o)][:80],'September 2026 nutrition brochure. Allergens not parsed.')
add('subway','Subway','https://media.subway.com/dam/urn:aaid:aem:f20a4541-8c88-496b-940d-4aa8318cae26/original/as/us-nutrition-en.pdf',[norm(o) for o in load('subway.raw.json') if o['name'].startswith('6"') and keep(o)],'6-inch subs as listed (footlong = double). Allergens not parsed.')
bw=[o for o in load('bww.raw.json') if keep(o,250) and not re.search(r'(?i)key on page|add |count (boneless|bone-in|traditional)|^\d+ count|wings,',o['name']) and len(o['name'])<60]
add('buffalo-wild-wings','Buffalo Wild Wings','https://www.buffalowildwings.com/nutrition/ (Nutrition Guide 08-18-2026 to 11-17-2026)',[norm(o) for o in bw],'Wing counts excluded (values depend on sauce choice). Allergens not parsed.')
dk=[o for o in load('dunkin.raw.json') if re.search(r'(?i)sandwich|wrap|bagel|hash|bowl|wake|grilled cheese|toast|croissant|omelet|bites',o['name']) and not re.search(r'(?i)\b(on|with|and|&)$',o['name'].strip()) and keep(o)]
add('dunkin',"Dunkin'",'https://www.dunkindonuts.com/en/menu/nutrition (DD nutrition guide PDF)',[norm(o) for o in dk],'Food items only. Allergens not parsed.')
BRAND={'chick-fil-a':['chick-fil-a'],'kfc':['kfc','taco bell/kfc'],'burger-king':['burger king'],'waffle-house':['waffle house'],'mcdonalds':["mcdonald's",'mcdonalds'],'sonic':['sonic','sonic drive-in'],'subway':['subway'],'buffalo-wild-wings':['buffalo wild wings','bww'],'dunkin':["dunkin'",'dunkin']}
for k,v in BRAND.items(): C[k]['match']=v
unsourced={"Wendy's":'No official US nutrition page/PDF reachable (site pages 404).','Taco Bell':'Official menu API exposes calories only.',"Arby's":'Official API values looked inconsistent; not used.','Popeyes':'Nutrition explorer data did not load headlessly.','Chipotle':'Official data is per ingredient only (build-your-own).',"Jack in the Box":'Two-column PDF could not be parsed reliably.','Firehouse Subs':'Only 4 items captured.',"Zaxby's":'PDF blocked from download.',"Raising Cane's":'Nutrition page returned 404.','Dairy Queen':'Food page did not yield data.','Starbucks':'Food nutrition PDF not found (link gave a corporate report).'}
json.dump(dict(generated='2026-10-24',chains=C,unsourced=unsourced),open('data/nutrition.json','w'),indent=0,ensure_ascii=False)
for k,v in C.items(): print(k,len(v['items']))
