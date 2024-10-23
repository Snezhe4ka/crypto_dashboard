import os
import json
import time

# TODO Do it later
CACHE_DIR = 'cache'
CACHE_EXPIRY = 3600

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def get_cache_filename(key):
    return os.path.join(CACHE_DIR, f"{key}.json")

def set_cache(key, data):
    cache_file = get_cache_filename(key)
    with open(cache_file, 'w') as f:
        json.dump({'timestamp': time.time(), 'data': data}, f)

def get_cache(key):
    cache_file = get_cache_filename(key)
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            cache_content = json.load(f)
            if time.time() - cache_content['timestamp'] < CACHE_EXPIRY:
                return cache_content['data']
    return None
