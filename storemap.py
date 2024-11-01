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

UNKNOWN_LOCATION = {
    # not defined
    "TOM'S WORLD (E-SQUARE@KEELUNG)": [25.1301738,121.7406039],
    "TOM'S WORLD(SHANG-SHUN WORLD@MIAOLI)": [24.6890502,120.9014187],
    "GiGO MITSUI OUTLET PARK Lin Kou": [25.0706472,121.364833],
    "QUANTUM GREENHILLS": [14.6025933,121.0494889],
    "QUANTUM SM FAIRVIEW": [14.7342227,121.0548111],
    "PALO Sunway Velocity Mall": [3.1278768,101.722265],
    "PALO Imago": [5.9708238,116.0611211],
    "FUNHOUSE SUNNYBANK": [-27.5710502,153.0606721],
    # wrong location
    "TOM'S WORLD (HAIDIAN-LI@TAINAN))": [23.026179,120.190815],
    "ROBOT AMUSEMENT": [16.7832939,96.1714648],
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
            if game_type == available_games[0]:
                continue
            tmp = find_duplicate_store(tmp, filter_country(stores[game_type], country))
        result.extend(tmp)

    # Save to file
    with open("json/duplicate.json", mode="w", encoding="utf-8") as store_file:
        store_file.write(json.dumps(result))
    return True


def parse_location(response, country):
    """
    Parse URLs, get addresses
    """
    result = []
    store_location = re.findall(r'//maps.google.com/maps\?q=(.*)\&zoom', response)
    store_address = re.findall(r'<span class="store_address">(.*)</span>', response)
    for i, _raw in enumerate(store_location):
        store_name, store_location = _raw.rsplit("@", 1)
        store_location = [float(i) for i in store_location.split(",")]

        if store_name in UNKNOWN_LOCATION:
            store_location = UNKNOWN_LOCATION[store_name]

        result.append({
            'name': store_name,
            'address': store_address[i],
            'location': store_location,
            'country': country
        })
    return result


def crawl_location(store_urls):
    """ (str) -> json

    Crawl from location.am-all.net
    """
    result = []

    for country in ["JP", "EN"]:
        if country == "JP":
            # Grab all prefectures (JP)
            if not store_urls.get("JP"):
                break
            for prefecture in range(47):
                response = requests.get(store_urls["JP"].format(prefecture=prefecture)).text
                result.extend(parse_location(response, country))

        elif country == "EN":
            # Grab all countries (EN)
            if not store_urls.get("EN"):
                break
            for country_id in range(1000, 1020):
                response = requests.get(store_urls["EN"].format(country=country_id)).text
                result.extend(parse_location(response, country))

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
