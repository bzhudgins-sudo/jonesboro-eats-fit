#!/usr/bin/env python3
"""Build data/restaurants.json from DoorDash's public AR store sitemap (Jonesboro slugs), deduped by brand.
Usage: python3 scripts/build-doordash.py [--fetch]"""
import re, json, sys, html, urllib.request, datetime, collections, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW=os.path.join(ROOT,'scripts/raw/doordash-jonesboro-store-urls.txt')
SITEMAP='https://cdn.doordash.com/sitemaps/sitemaps/sitemap-doordash-ar-stores.xml'
if '--fetch' in sys.argv:
    x=urllib.request.urlopen(urllib.request.Request(SITEMAP,headers={'User-Agent':'Mozilla/5.0'})).read().decode()
    urls=[html.unescape(u) for u in re.findall(r'<loc>([^<]*jonesboro[^<]*)</loc>',x) if '/store/' in u and '/convenience/' not in u]
    open(RAW,'w').write('\n'.join(urls)+'\n')
urls=[html.unescape(l.strip()) for l in open(RAW) if l.strip()]
# Not restaurants (flowers, markets, carts, grocery, catering/meal-prep services)
EXCLUDE={'24-hours-cart','adams-market','angel-market',"bennett's-flowers",'bloom-haus-by-kroger','los-arcos-mexican-store','meals-for-moms','garrett-cooking-n-catering-llc','livelihood-llc',"catering-by-steak-'n-shake"}
NAMES={"arby's":"Arby's","auntie-annes":"Auntie Anne's","chick-fil-a":"Chick-fil-A","chuck-e.-cheese":"Chuck E. Cheese","dunkin'":"Dunkin'","domino's":"Domino's","ihop":"IHOP","kfc":"KFC","mcdonald's":"McDonald's","qdoba-mexican-eats":"Qdoba Mexican Eats","omt":"OMT","zaxbys":"Zaxby's","papa-johns-pizza":"Papa Johns Pizza","t-tea-jonesboro":"T Tea","tjs-burgers":"TJ's Burgers","j-j-wings":"J J Wings","j-&-bs-twizted-barbecue":"J & B's Twizted Barbecue","ba-burrito":"BA Burrito","ba-eats":"BA Eats","a1-sushi-and-hibachi":"A1 Sushi and Hibachi","mlb-ballpark-bites":"MLB Ballpark Bites","kpot-korean-bbq-&-hot-pot":"KPOT Korean BBQ & Hot Pot","ohana-hawaiin-snow":"Ohana Hawaiian Snow","tops-bar-b-q":"Tops Bar-B-Q","que-49-smokehouse":"Que 49 Smokehouse","ed's-catfish.":"Ed's Catfish","sladers-alaskan-dumpling-co.":"Slader's Alaskan Dumpling Co.","love's-donut--kolaches,-smoothies-and-boba-tea":"Love's Donut, Kolaches, Smoothies and Boba Tea","rons-catfish":"Ron's Catfish","ginas-place":"Gina's Place","delilahs-ice-cream":"Delilah's Ice Cream","partovis-gyros":"Partovi's Gyros","papitos-mexican-grill":"Papito's Mexican Grill","carroll's-candies":"Carroll's Candies","rock-n-roll-sushi-&-hibachi":"Rock N Roll Sushi & Hibachi","fizzle-up":"Fizzle Up","jtown's-grill":"JTown's Grill","hoodrolls":"HoodRolls","deso-chocolate":"DeSo Chocolate","sonic-drive-in":"Sonic Drive-In","hunters-loaded-lemonade":"Hunter's Loaded Lemonade"}
SMALL={'and','of','the','n','y','de','by','in','to','for'}
def slug_brand(u):
    s=re.sub(r'^.*/store/','',u).rstrip('/')
    s=re.sub(r'-jonesboro-\d+$','',s)
    s=re.sub(r'---.*$','',s)              # "name---address"
    s=re.sub(r'-?\(.*?\)','',s)           # "(jonesboro)" / "(305 s main st)"
    s=re.sub(r'-ar$','',s).strip('-')
    return s
def title(s):
    if s in NAMES: return NAMES[s]
    w=[x for x in re.split(r'-+',s) if x]
    out=[]
    for i,x in enumerate(w):
        t=x if x=='&' else (x if (i and x in SMALL) else x[:1].upper()+x[1:])
        out.append(t)
    r=' '.join(out)
    r=re.sub(r' Llc$','',r); r=r.replace('Bbq','BBQ')
    return r
groups=collections.OrderedDict()
for u in urls:
    b=slug_brand(u)
    if b in EXCLUDE: continue
    key=re.sub(r'[^a-z0-9]','',b)
    groups.setdefault(key,{'slug':b,'urls':[]})['urls'].append(u)
rest=[]
# Places with existing nutrition data that have no Jonesboro DoorDash page — kept so no data is lost
EXTRA=[('wafflehouse','Waffle House'),('nativebrewworks','Native Brew Works'),('501steakhouse','501 Steakhouse')]
for key,g in sorted(groups.items()):
    rest.append({'id':key,'name':title(g['slug']),'locations':len(g['urls']),'doordash':g['urls'][0],'doordash_all':g['urls']})
for k,n in EXTRA:
    if k not in groups: rest.append({'id':k,'name':n,'locations':0,'doordash':None,'doordash_all':[]})
rest.sort(key=lambda r:r['name'].lower())
out={'generated':datetime.date.today().isoformat(),'source':SITEMAP+' (public DoorDash store sitemap, URLs whose slug contains "jonesboro"; restaurant /store/ pages only, convenience/grocery excluded)',
     'doordash_store_pages':len(urls),'excluded_non_restaurants':sorted(EXCLUDE),'restaurants':rest}
json.dump(out,open(os.path.join(ROOT,'data/restaurants.json'),'w'),indent=1,ensure_ascii=False)
print(len(urls),'store pages ->',len(rest),'brands')
