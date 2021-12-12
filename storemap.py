#!/usr/bin/python -u
#-*- coding: utf-8 -*-
# <?php exit;

"""
storemap.py

SEGA storemap crawler
"""

import re
import json
import requests

STORES = {
    "ongeki": "https://location.am-all.net/alm/location?gm=88&at={prefecture}&ct=1000",
    "chunithm": "https://location.am-all.net/alm/location?gm=109&lang=en&ct=1000&at={prefecture}",
    "maimai": "https://location.am-all.net/alm/location?gm=96&lang=en&ct=1000&at={prefecture}",
}

def dupe_stores():
    """
    Find duplicate stores
    """
    def _find_dupe_store(store_a, store_b):
        """ (list of dict, list of dict) -> list of dict

        Find duplicate dictionaries in two lists of dictionaries
        """
        result = []
        _tmp = set((_find['name'], tuple(_find['address'])) for _find in store_a)
        for _find in store_b:
            if (_find['name'], tuple(_find['address'])) in _tmp:
                result.append(_find)
        return result

    # Load store files
    _stores = []
    for store in STORES:
        with open(f"json/{store}.json", encoding="utf-8") as store_file:
            _stores.append(json.loads(store_file.read()))
    # Use _find_dupe_store to catch duplicates
    result = _stores[0]
    for i in range(1, len(_stores)):
        result = _find_dupe_store(result, _stores[i])
    # Save to file
    with open("json/duplicate.json", mode="w", encoding="utf-8") as store_file:
        store_file.write(json.dumps(result))
    return True

def crawl_stores():
    """
    Crawl stores and save to file
    """
    def _crawl_location(url):
        """ (str) -> json

        Crawl from location.am-all.net
        """
        result = []
        # Grab all prefectures
        for _prefecture in range(47):
            # Parse URLs, get addresses
            resp_text = requests.get(url.format(prefecture=_prefecture)).text
            _loc = re.findall(r'//maps.google.com/maps\?q=(.*)\&zoom', resp_text)
            _addr = re.findall(r'<span class="store_address">(.*)</span>', resp_text)
            for i, _raw in enumerate(_loc):
                _name, _location = _raw.split("@")
                _location = [float(i) for i in _location.split(",")]
                result.append({
                    'name': _name,
                    'address': _addr[i],
                    'location': _location,
                })
        return result

    for store_name, store_url in STORES.items():
        with open(f"json/{store_name}.json", mode="w", encoding="utf-8") as store_file:
            _result = _crawl_location(store_url)
            store_file.write(json.dumps(_result))

    return True

if __name__ == "__main__":
    crawl_stores()
    dupe_stores()
