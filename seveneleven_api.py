import requests
import sqlite3 as sl

class CustomException(Exception):
    """Custom exception class"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

con = sl.connect('fortnite.db', isolation_level=None)
cursor = con.cursor()

def check_lowest_fuel_price():
    try:
        stores = requests.get("https://www.7eleven.com.au/storelocator-retail/mulesoft/stores?lat=-33.8688197&long=151.2092955&dist=512")
        stores = stores.json()
        stores = stores['stores']
        fuel_stores = []
        for store in stores:
            if len(store['fuelOptions']) > 0:
                fuel_stores.append({
                    'id': store['storeId'],
                    'name': store['name'],
                    'location': store['location']
                })

        # ean 52 = 91
        # ean 57 = e10

        prices = []

        for store in fuel_stores:
            result = requests.get(f"https://www.7eleven.com.au/storelocator-retail/mulesoft/fuelPrices?storeNo={store['id']}")
            if result.status_code != 200:
                print(result.status_code)
            result = result.json()
            for item in result['data']:
                if item['ean'] in ['52', '57']:
                    prices.append({
                        'price': item['price'],
                        'name': store['name'],
                        'location': store['location']
                    })

        min_price_item = min(prices, key=lambda x: x['price'])

        return f"Found prices for {len(prices)} stores. Cheapest is selling for {(min_price_item['price'])/10}c/l at {min_price_item['name']} {min_price_item['location']}."
    except Exception as e:
        return e

def check_lowest_fuel_price_p03():
    attempted_json = False
    try:
        response = requests.get("https://projectzerothree.info/api.php?format=json")
        response = response.json()
        attempted_json = True
        updated = response['updated']
        cheapest_nsw = response['regions'][2]
        min_price = min(filter(lambda x: x["type"] in ["E10", "U91"], cheapest_nsw["prices"]),key=lambda x: x["price"])
        return min_price, updated
    except Exception as e:
        if not attempted_json:
            try:
                raise CustomException("Unable to access respons json. Object not subscriptable")
            except Exception as e:
                return e
        return e