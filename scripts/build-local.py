# Local restaurant ESTIMATES (not restaurant-provided). Dishes transcribed from real menus (URLs recorded);
# macros estimated from typical recipes/portions using USDA FoodData Central generic (SR Legacy/Foundation) foods.
import json,re
def I(name,cal,p,c,f,portion,al):
  return dict(name=name,cal=cal,protein=p,carbs=c,fat=f,portion=portion,allergens=al)
L={}
L['hong-kong']=dict(name='Hong Kong',match=['hong kong'],menu_source='https://www.hongkong3228.com/ (online order menu, viewed 2026-10-24)',items=[
I('Chicken w. Broccoli (large, no rice)',620,55,30,30,'~1 qt: 8 oz chicken breast, 2 cups broccoli, brown sauce, oil',['soy','gluten']),
I('Beef w. Broccoli (large, no rice)',720,50,32,42,'~1 qt: 8 oz flank steak, 2 cups broccoli, brown sauce',['soy','gluten']),
I('Shrimp w. Broccoli (large, no rice)',480,45,30,18,'~1 qt: 8 oz shrimp, 2 cups broccoli, brown sauce',['shellfish','soy','gluten']),
I('Moo Goo Gai Pan (large, no rice)',560,50,28,26,'~1 qt: chicken, mushrooms, mixed veg, white sauce',['soy','carrot']),
I('Vegetable Delight (large, no rice)',380,12,45,18,'~1 qt mixed vegetables, white sauce',['soy','carrot']),
I('Steamed Dumplings (8)',420,20,48,16,'8 pork dumplings ~30 g each',['gluten','soy']),
I('Wonton Soup (small)',180,12,20,5,'~2 cups broth, 6 wontons',['gluten','egg','soy']),
I('Hot & Sour Soup (small)',160,9,18,6,'~2 cups',['soy','egg','gluten','carrot']),
I('Chicken Fried Rice (large)',1100,45,150,35,'~1 qt fried rice with egg and chicken',['egg','soy','carrot']),
I('Chicken Lo Mein (large)',1050,45,140,35,'~1 qt noodles, chicken, cabbage, carrot',['gluten','egg','soy','carrot']),
I('Sesame Chicken (large, no rice)',1250,55,130,55,'~1 qt battered fried chicken, sweet sauce',['gluten','egg','soy','sesame']),
I("General Tso's Chicken (large, no rice)",1300,55,130,60,'~1 qt battered fried chicken, sweet-spicy sauce',['gluten','egg','soy']),
I('Sweet & Sour Chicken (large, no rice)',1200,45,150,45,'~1 qt battered chicken, sweet & sour sauce',['gluten','egg','tomato','fruit']),
I('Kung Pao Chicken (large, no rice)',800,55,35,50,'~1 qt chicken, peanuts, veg',['peanut','soy','gluten','carrot']),
I('Pepper Steak w. Onions (large, no rice)',650,45,30,38,'~1 qt beef, peppers, onions, brown sauce',['soy','gluten']),
I('Egg Roll (each)',200,6,22,10,'1 roll ~85 g',['gluten','egg','soy','carrot']),
I('Crab Rangoon (10)',700,16,60,44,'10 fried cream-cheese wontons',['gluten','dairy','egg','shellfish']),
I('Steamed white rice (pint)',410,8,90,1,'~2 cups cooked',[]),
])
L['native-brew-works']=dict(name='Native Brew Works',match=['native brew works'],menu_source='https://nativebrewworks.com/menu (viewed 2026-10-24)',items=[
I('Waco (waffle with eggs, bacon, cheese; syrup on side)',780,32,60,45,'1 waffle, 2 eggs, 2 strips bacon, 1 oz cheese; syrup excluded',['gluten','egg','dairy']),
I('Brunch Bowl (potatoes, pulled pork, black beans, egg)',820,40,75,38,'~1.5 cups potatoes, 4 oz pork, 1/2 cup beans, 1 egg, sour cream, queso fresco',['egg','dairy']),
I('Brunch Burger with breakfast potatoes',1150,48,70,72,'1/3 lb patty, cheese, bacon, egg, sauce, bun, 1 cup potatoes',['gluten','egg','dairy']),
I('Burger (cheese, lettuce, tomato, pickled onion)',780,38,45,46,'1/3 lb patty, cheese, bun, mayo',['gluten','egg','dairy','tomato']),
I('Taco Salad (chicken)',650,40,40,36,'romaine, 5 oz chicken, beans, cheese, pico, tortilla strips; no dressing',['dairy','tomato','carrot']),
I('Loaded Queso (with chips)',950,30,70,60,'~1 cup queso with beef & corn, ~2 oz chips',['dairy','tomato']),
])
L['501-steakhouse']=dict(name='501 Steakhouse',match=['501 steakhouse'],menu_source='https://501steakhouse.com/ and https://501steakhouse.com/menu (viewed 2026-10-24)',items=[
I('14oz House Dry Aged Ribeye w/ asparagus & twice baked potato',1450,90,45,100,'14 oz raw ribeye, garlic butter, 1 cup asparagus, loaded twice-baked potato',['dairy']),
I('Salmon Piccata over angel hair',1050,50,85,52,'7 oz salmon, 1.5 cups pasta, butter-caper sauce',['fish','gluten','dairy']),
I('Seared Ahi Tuna (starter)',280,40,8,8,'~6 oz tuna, soy ginger sauce',['fish','soy','gluten']),
I('Classic Shrimp Cocktail',220,30,18,2,'~8 jumbo shrimp, cocktail sauce',['shellfish','tomato']),
I('Jumbo Maryland Lump Crabcake (2)',700,35,40,44,'2 crab cakes ~4 oz each, fried eggplant, meunière sauce',['shellfish','egg','gluten','dairy']),
I('Herbed Goat Cheese & Bacon Filet Burger w/ fries',1250,55,95,70,'6 oz patty, goat cheese, bacon, bun, ~5 oz fries',['gluten','dairy','tomato']),
I('Bang Bang Shrimp',650,25,45,40,'~10 fried shrimp, creamy chili sauce',['shellfish','gluten','egg']),
])
d=json.load(open('data/local-don-jose.json'))
FR=r'salsa|pico|guac|avocado|tomato|rotel|enchilada|taco salad|club salad|tossed salad|marinara|ketchup|ranchero'
def tag(n,base):
  s=set(base or []);t=n.lower()
  if re.search(r'salsa|pico|tomato|rotel|enchilada|ranchero|marinara|ketchup|salad|rice|taco|burrito|chips',t): s.add('tomato')
  if re.search(r'guac|avocado|salad',t): s.add('fruit')
  if re.search(r'salad',t): s.add('carrot')
  return sorted(s)
dj=[]
for i in d['items']:
  base=['dairy'] if re.search(r'(?i)cheese|quesadilla|enchilada|burrito|dip',i['name']) else []
  if re.search(r'(?i)burrito|quesadilla|enchilada|taco',i['name']): base.append('gluten')
  i['allergens']=tag(i['name'],base)
  dj.append(dict(name=i['name'],cal=i['calories_est'],protein=i['protein_g_est'],carbs=i['carbs_g_est'],fat=i['fat_g_est'],allergens=i['allergens']))
d['retagged']='2026-10-24: tomato/fresh fruit/carrot tags added (likely, from typical recipes)'
json.dump(d,open('data/local-don-jose.json','w'),indent=1)
L['don-jose']=dict(name='Don Jose Mexican Restaurant',match=['don jose'],menu_source=' ; '.join(d['menu_sources']),items=dj)
for v in L.values(): v['label']='Estimated'
json.dump(dict(generated='2026-10-24',method='Estimated: dishes come from the restaurant\'s real menu (source recorded). Calories/macros are estimated from typical recipes and portion sizes using USDA FoodData Central generic foods. They are not restaurant-provided and can be off by 20-30%. Allergen tags (incl. tomato, fresh fruit, carrot) are "likely" based on typical recipes — always ask your server.',restaurants=L),open('data/local-estimates.json','w'),indent=1,ensure_ascii=False)
print({k:len(v['items']) for k,v in L.items()})
