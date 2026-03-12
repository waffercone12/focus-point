import json
import requests

def load_data():
    with open('recipes.json') as f: recipes = json.load(f)
    with open('constants.json') as f: constants = json.load(f)
    return recipes, constants

def get_live_prices(item_ids, city="FortSterling"):
    """Fetches real-time prices from the Albion Data Project API."""
    url = f"https://west.albion-online-data.com/api/v2/stats/prices/{item_ids}?locations={city}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # We take sell_price_min as the current market cost
            return {item['item_id']: item['sell_price_min'] for item in data}
    except Exception as e:
        print(f"Market API Error: {e}")
    return {}

def calculate_plan(item_key, amount, city="fort_sterling", use_focus=False):
    recipes, consts = load_data()
    recipe = recipes[item_key]
    
    rrr = consts['rrr']['city_focus'] if use_focus else consts['rrr']['city_no_focus']
    batches = amount / recipe['yield']
    
    # 1. Ingredient Calculation
    raw_needs = {ing: round((qty * batches) * (1 - rrr)) for ing, qty in recipe['ingredients'].items()}
    
    # 2. Get Live Market Data
    all_ids = ",".join([recipe['id']] + list(raw_needs.keys()))
    prices = get_live_prices(all_ids)

    # 3. Farming & Profit Logic
    plan = {"name": recipe['name'], "farming": {}, "total_cost": 0, "market_value": 0}
    
    for mat, qty in raw_needs.items():
        price = prices.get(mat, 0)
        plan['total_cost'] += (qty * price)
        
        # Farming logic for animals
        if mat in recipe.get('animal_source', {}):
            src = recipe['animal_source'][mat]
            animal_count = round(qty / consts['farming']['animal_yield_avg'])
            feed_bonus = consts['city_bonuses'].get(city, {}).get(src['feed'].lower(), 1.0)
            seeds = round((animal_count * consts['farming']['favorite_feed_requirement'] / consts['farming']['crop_yield_avg']) / feed_bonus)
            plan['farming'][mat] = {"animals": animal_count, "seeds": seeds, "feed": src['feed']}
        else:
            bonus = consts['city_bonuses'].get(city, {}).get(mat.lower(), 1.0)
            seeds = round((qty / consts['farming']['crop_yield_avg']) / bonus)
            plan['farming'][mat] = {"seeds": seeds}

    plan['market_value'] = amount * prices.get(recipe['id'], 0)
    plan['profit'] = plan['market_value'] - plan['total_cost']
    
    return plan