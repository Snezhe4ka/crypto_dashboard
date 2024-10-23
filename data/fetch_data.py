import requests
from dotenv import load_dotenv
import time
import logging
from cachetools import TTLCache
from typing import Dict, Any, Optional
from contextlib import contextmanager
from data import db_manager
import json
from datetime import datetime
from dateutil import parser
from sqlalchemy.exc import SQLAlchemyError


# PostgreSQL details
USERNAME = 'sni'
PASSWORD = ''
HOST = 'localhost'
PORT = '5432'
DATABASE = 'crypto_data'

DB_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

# Initialize the database
db_manager.initialize_db()

# Cache setup: cache size of 100, expiration time of 1 hour
cache = TTLCache(maxsize=500, ttl=3600)
COINGECKO_API = 'https://api.coingecko.com/api/v3'


def fetch_data_from_api(url, params: Optional[Dict[str, Any]] = None):
    retries = 4
    delay = 10  # Start with a 10-second delay
    if params is None:
        params = {}

    for i in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if response and response.status_code == 429:  # too Many Requests
                delay = min(delay * 2, 60)  # Increment the delay up to a max of 60 seconds
                logging.warning(f"Rate limit hit. Retrying in {delay} seconds... Attempt {i + 1}/{retries}")
                time.sleep(delay)
            else:
                status_code = response.status_code if response else 'No response'
                content = response.text if response else 'No response content'
                logging.error(f"Failed to fetch data from {url}. Status code: {status_code}. "
                              f"Error: {e}. Response content: {content}")
                return {}
    return None


def parse_datetime(date_value: Any) -> Optional[datetime]:
    if isinstance(date_value, int):
        return datetime.utcfromtimestamp(date_value)
    elif isinstance(date_value, str):
        try:
            return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
        except ValueError as e:
            print(f"Error parsing date string {date_value}: {e}")
    return None


# to fetch  data
def fetch_market_data():
    url = f"{COINGECKO_API}/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 100,
        'page': 1,
        # 'sparkline': 'true'  # To fetch sparkline data if needed
    }
    data = fetch_data_from_api(url, params)

    if data:
        processed_data = []
        for coin in data:
            coin_data = {
                "symbol": coin.get("symbol"),
                "name": coin.get("name"),
                "image": coin.get("image"),
                "current_price": coin.get("current_price"),
                "market_cap": coin.get("market_cap"),
                "market_cap_rank": coin.get("market_cap_rank"),
                "fully_diluted_valuation": coin.get("fully_diluted_valuation"),
                "total_volume": coin.get("total_volume"),
                "high_24h": coin.get("high_24h"),
                "low_24h": coin.get("low_24h"),
                "price_change_24h": coin.get("price_change_24h"),
                "price_change_percentage_24h": coin.get("price_change_percentage_24h"),
                "market_cap_change_24h": coin.get("market_cap_change_24h"),
                "market_cap_change_percentage_24h": coin.get("market_cap_change_percentage_24h"),
                "circulating_supply": coin.get("circulating_supply"),
                "total_supply": coin.get("total_supply"),
                "max_supply": coin.get("max_supply"),
                "ath": coin.get("ath"),
                "ath_change_percentage": coin.get("ath_change_percentage"),
                "ath_date": parse_datetime(coin.get("ath_date")),
                "atl": coin.get("atl"),
                "atl_change_percentage": coin.get("atl_change_percentage"),
                "atl_date": parse_datetime(coin.get("atl_date")),
                "roi": coin.get("roi"),
                "last_updated": parse_datetime(coin.get("last_updated")),
                "price_change_percentage_1h": coin.get("price_change_percentage_1h", None),  # Nullable
                "sparkline_in_7d": coin.get("sparkline_in_7d", None),  # Store as JSON if present
                "timestamp": datetime.utcnow()
            }
            processed_data.append(coin_data)

        # Insert the processed data into the database
        if data:
            db_manager.insert_market_data(data)
        else:
            print("API call failed. Keeping the last valid data intact")

    return data


def fetch_global_data():
    url = f"{COINGECKO_API}/global"
    response_data = fetch_data_from_api(url)

    if 'data' in response_data:
        global_data = response_data['data']
        processed_data = {
            "active_cryptocurrencies": global_data.get("active_cryptocurrencies"),
            "upcoming_icos": global_data.get("upcoming_icos"),
            "ongoing_icos": global_data.get("ongoing_icos"),
            "ended_icos": global_data.get("ended_icos"),
            "markets": global_data.get("markets"),
            "total_market_cap": global_data.get("total_market_cap"),  # Stored as JSON
            "total_volume": global_data.get("total_volume"),  # Stored as JSON
            "market_cap_percentage": global_data.get("market_cap_percentage"),  # Stored as JSON
            "market_cap_change_percentage_24h_usd": global_data.get("market_cap_change_percentage_24h_usd"),
            "updated_at": parse_datetime(global_data.get("updated_at")),
            "timestamp": datetime.utcnow()
        }

        # Insert processed data into the database
        db_manager.insert_global_data(processed_data)
    else:
        print("Error: 'data' field not found in response from /global endpoint")


def fetch_trending_data():
    url = f"{COINGECKO_API}/search/trending"
    data = fetch_data_from_api(url)

    if data and "coins" in data:
        trending_coins = []
        for coin in data["coins"]:
            item = coin.get("item", {})

            # # Parse the nested `data` field if it exists and is a string
            data_field = item.get("data", {})
            if isinstance(data_field, str):
                try:
                    data_field = json.loads(data_field)
                except json.JSONDecodeError:
                    data_field = {}

            # Extract relevant fields after parsing
            coin_data = {
                "coin_id": item.get("id"),
                "coin_name": item.get("name"),
                "symbol": item.get("symbol"),
                "market_cap_rank": item.get("market_cap_rank"),
                "small": item.get("small"),
                "score": item.get("score"),
                # "price_change_percentage_24h": data_field.get("price_change_percentage_24h"),
                "price": data_field.get("price", None),
                "market_cap": data_field.get("market_cap", '').replace('$', '').replace(',', ''),
                "total_volume": data_field.get("total_volume", None),
                "timestamp": datetime.utcnow()
            }
            trending_coins.append(coin_data)

        db_manager.insert_trending_coins(trending_coins)

    return trending_coins


def fetch_market_dominance():
    url = f"{COINGECKO_API}/global"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get('data', {})
        market_cap_percentage = data.get('market_cap_percentage', {})

        market_dominance_data = {
            'btc': market_cap_percentage.get('btc', 0),
            'eth': market_cap_percentage.get('eth', 0),
            'usdt': market_cap_percentage.get('usdt', 0),
            'usdc': market_cap_percentage.get('usdc', 0),
            'bnb': market_cap_percentage.get('bnb', 0),
            'sol': market_cap_percentage.get('sol', 0),
            'xrp': market_cap_percentage.get('xrp', 0),
            'others': 100 - (
                    market_cap_percentage.get('btc', 0) +
                    market_cap_percentage.get('eth', 0) +
                    market_cap_percentage.get('usdt', 0) +
                    market_cap_percentage.get('usdc', 0) +
                    market_cap_percentage.get('bnb', 0) +
                    market_cap_percentage.get('sol', 0) +
                    market_cap_percentage.get('xrp', 0)
            ),
            'timestamp': datetime.utcnow()
        }

        # Insert data into the database
        db_manager.insert_market_dominance(market_dominance_data)


def fetch_category_data():
    url = f"{COINGECKO_API}/coins/categories"
    data = fetch_data_from_api(url)

    if data:
        processed_data = []
        for category in data:
            category_data = {
                "category_id": category.get("id"),  # Maps to 'category_id' in Categories
                "name": category.get("name"),
                "market_cap": category.get("market_cap"),
                "market_cap_24h_change": category.get("market_cap_change_24h"),  # Corrected to match the field name
                "top_3_coins": json.dumps(category.get("top_3_coins", [])),  # Serialize as JSON
                "volume_24h": category.get("volume_24h"),
                "timestamp": datetime.utcnow()  # Manually add timestamp
            }
            processed_data.append(category_data)

        db_manager.insert_category_data(processed_data)

    return data

def fetch_coin_symbols():
    url = f"{COINGECKO_API}/coins/id"
    data = fetch_data_from_api(url)

    if data:
        processed_data = []
        for symbols in data:
            symbols_data = {
                "symbol_id": symbols.get("id"),
                "symbol": symbols.get("symbol"),
                "name": symbols.get("name"),
                "market_cap": symbols.get("market_cap"),
                "categories": json.dumps(symbols.get("categories", [])),
                "image": json.dumps(symbols.get("image", {})),
                "price_change_percentage_24h": symbols.get("price_change_percentage_24h"),
                "price_change_percentage_7d": symbols.get("price_change_percentage_7d"),
                "market_cap_change_24h": symbols.get("market_cap_change_24h"),
                "market_cap_change_percentage_24h": symbols.get("market_cap_change_percentage_24h"),
                "market_cap_24h_change": symbols.get("market_cap_change_24h"),  # Corrected to match the field name
                "timestamp": datetime.utcnow()  # Manually add timestamp
            }
            processed_data.append(symbols_data)

        db_manager.insert_symbols_data(processed_data)

    return data


# def main():
#     print("START")
# initialize the database
db_manager.initialize_db()


# Fetch market data and store it in the database
# print("Fetching market data...")
market_data = fetch_market_data()

# Fetch and store global crypto data
global_data = fetch_global_data()

# Fetch and store trending data
trending_data = fetch_trending_data()

market_dominance = fetch_market_dominance()
# print("market_dominance Data:", market_dominance)

# Fetch and store all coin categories
# print("Fetching coin categories...")
category_data = fetch_category_data()

top_projects_by_volume = db_manager.insert_top_projects_by_volume()
top_gainers_market_cap = db_manager.insert_top_gainers_market_cap()
#
# if __name__ == "__main__":
#     main()
