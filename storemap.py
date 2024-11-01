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
    "ongeki": {
        "JP": "https://location.am-all.net/alm/location?gm=88&at={prefecture}&ct=1000",
    },
    "chunithm": {
        "JP": "https://location.am-all.net/alm/location?gm=109&lang=en&ct=1000&at={prefecture}",
        "EN": "https://location.am-all.net/alm/location?gm=104&lang=en&ct={country}",
    },
    "maimai": {
        "JP": "https://location.am-all.net/alm/location?gm=96&lang=en&ct=1000&at={prefecture}",
        "EN": "https://location.am-all.net/alm/location?gm=98&lang=en&ct={country}",
    },
}


def find_duplicate_store(store_a, store_b):
    """ (list of dict, list of dict) -> list of dict

    Find duplicate dictionaries in two lists of dictionaries
    """
    result = []
    _tmp = set((_find['name'], tuple(_find['address'])) for _find in store_a)
    for _find in store_b:
        if (_find['name'], tuple(_find['address'])) in _tmp:
            result.append(_find)
    return result


def dupe_stores():
    """
    Find duplicate stores
    """
    # filter by country
    def filter_country(store_list, country):
        return list(filter(lambda d: d['country'] == country.upper(), store_list))

    # Load store files
    stores = {}
    for game_type in STORES:
        with open(f"json/{game_type}.json", encoding="utf-8") as store_file:
            stores[game_type] = json.loads(store_file.read())

    # find duplicate store to catch duplicates
    result = []
    for country in ["JP", "EN"]:
        available_games = [i for i in STORES if STORES[i].get(country)]

        tmp = filter_country(stores[available_games[0]], country)
        for game_type in available_games:
            tmp = find_duplicate_store(tmp, filter_country(stores[game_type], country))
        result.extend(tmp)

    # Save to file
    with open("json/duplicate.json", mode="w", encoding="utf-8") as store_file:
        store_file.write(json.dumps(result))
    return True


def crawl_location(store_urls):
    """ (str) -> json

    Crawl from location.am-all.net
    """
    result = []

    # Grab all prefectures (JP)
    if store_urls.get("JP"):
        for prefecture in range(47):
            # Parse URLs, get addresses
            response = requests.get(store_urls["JP"].format(prefecture=prefecture)).text
            store_location = re.findall(r'//maps.google.com/maps\?q=(.*)\&zoom', response)
            store_address = re.findall(r'<span class="store_address">(.*)</span>', response)
            for i, _raw in enumerate(store_location):
                store_name, store_location = _raw.split("@")
                store_location = [float(i) for i in store_location.split(",")]
                result.append({
                    'name': store_name,
                    'address': store_address[i],
                    'location': store_location,
                    'country': 'JP'
                })

    # Grab all countries (EN)
    if store_urls.get("EN"):
        for country in range(1000, 1020):
            response = requests.get(store_urls["EN"].format(country=country)).text
            store_location = re.findall(r'//maps.google.com/maps\?q=(.*)\&zoom', response)
            store_address = re.findall(r'<span class="store_address">(.*)</span>', response)
            for i, _raw in enumerate(store_location):
                store_name, store_location = _raw.rsplit("@", 1)
                store_location = [float(i) for i in store_location.split(",")]
                result.append({
                    'name': store_name,
                    'address': store_address[i],
                    'location': store_location,
                    'country': 'EN'
                })
    return result


def crawl_stores():
    """
    Crawl stores and save to file
    """

    for game_name, store_urls in STORES.items():
        with open(f"json/{game_name}.json", mode="w", encoding="utf-8") as store_file:
            result = crawl_location(store_urls)
            store_file.write(json.dumps(result))

    return True


if __name__ == "__main__":
    crawl_stores()
    dupe_stores()
