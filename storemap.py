#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
storemap.py

SEGA storemap crawler
"""

import re
import json
import requests
from typing import List, Dict, Any

# List of url templates for SEGA games with different regions
STORES: Dict[str, Dict[str, str]] = {
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

# Hardcoded coordinates for stores with ambiguous or wrong locations.
UNKNOWN_LOCATION: Dict[str, List[float]] = {
    # Not defined on the map
    "TOM'S WORLD (E-SQUARE@KEELUNG)": [25.1301738, 121.7406039],
    "TOM'S WORLD(SHANG-SHUN WORLD@MIAOLI)": [24.6890502, 120.9014187],
    "GiGO MITSUI OUTLET PARK Lin Kou": [25.0706472, 121.364833],
    "QUANTUM GREENHILLS": [14.6025933, 121.0494889],
    "QUANTUM SM FAIRVIEW": [14.7342227, 121.0548111],
    "PALO Sunway Velocity Mall": [3.1278768, 101.722265],
    "PALO Imago": [5.9708238, 116.0611211],
    "FUNHOUSE SUNNYBANK": [-27.5710502, 153.0606721],
    # Incorrect locations
    "TOM'S WORLD (HAIDIAN-LI@TAINAN))": [23.026179, 120.190815],
    "ROBOT AMUSEMENT": [16.7832939, 96.1714648],
}


def find_duplicate_store(store_a: List[Dict[str, Any]],
                         store_b: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Find duplicate store entries between two lists based on their address.
    """
    addresses_a = {tuple(store["address"]) for store in store_a}
    return [store for store in store_b if tuple(store["address"]) in addresses_a]


def filter_by_country(store_list: List[Dict[str, Any]], country: str) -> List[Dict[str, Any]]:
    """
    Filter a list of store dictionaries by country (case-insensitive).
    """
    country_upper = country.upper()
    return [store for store in store_list if store.get("country", "").upper() == country_upper]


def dupe_stores() -> bool:
    """
    Load all store files, find duplicates across games for each country,
    and save the duplicates to 'json/duplicate.json'.
    """
    # Load store data from JSON files.
    stores: Dict[str, List[Dict[str, Any]]] = {}
    for game_type in STORES:
        file_path = f"json/{game_type}.json"
        with open(file_path, encoding="utf-8") as store_file:
            stores[game_type] = json.load(store_file)

    duplicates: List[Dict[str, Any]] = []
    for country in ["JP", "EN"]:
        # Find games with a URL for the specified country.
        available_games = [game for game in STORES if country in STORES[game]]
        if not available_games:
            continue

        # Use the first game's stores as the initial set.
        common_stores = filter_by_country(stores[available_games[0]], country)
        for game in available_games[1:]:
            common_stores = find_duplicate_store(
                common_stores, filter_by_country(stores[game], country)
            )
        duplicates.extend(common_stores)

    with open("json/duplicate.json", "w", encoding="utf-8") as dup_file:
        json.dump(duplicates, dup_file, ensure_ascii=False, indent=2)
    return True


def parse_location(response_text: str, country: str) -> List[Dict[str, Any]]:
    """
    Parse the HTML response to extract store information.

    Args:
        response_text: The HTML content returned from the location URL.
        country: The country code ("JP" or "EN").

    Returns:
        A list of dictionaries, each containing the store's name, address, location, and country.
    """
    results: List[Dict[str, Any]] = []
    # Extract the portion containing the coordinates.
    location_matches = re.findall(r'//maps.google.com/maps\?q=(.*)&zoom', response_text)
    # Extract the store addresses.
    address_matches = re.findall(r'<span class="store_address">(.*)</span>', response_text)

    for idx, raw_location in enumerate(location_matches):
        # Expecting format: "store_name@lat,lng"
        try:
            store_name, coords_str = raw_location.rsplit("@", 1)
            coords = [float(coord) for coord in coords_str.split(",")]
        except ValueError:
            # Skip malformed entries.
            continue

        # Override with known correct coordinates if available.
        if store_name in UNKNOWN_LOCATION:
            coords = UNKNOWN_LOCATION[store_name]

        # Ensure we have a matching address.
        address = address_matches[idx] if idx < len(address_matches) else ""

        results.append({
            "name": store_name,
            "address": address,
            "location": coords,
            "country": country
        })
    return results


def crawl_location(store_urls: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Crawl the store locations from the provided URL templates.

    Args:
        store_urls: A dictionary with country codes as keys and URL templates as values.

    Returns:
        A list of store dictionaries with name, address, location, and country.
    """
    all_stores: List[Dict[str, Any]] = []
    # Define the range of IDs for each country.
    id_ranges: Dict[str, range] = {
        "JP": range(47),         # Japanese prefectures range.
        "EN": range(1000, 1020),   # English country IDs range.
    }

    for country, ids in id_ranges.items():
        url_template = store_urls.get(country)
        if not url_template:
            continue  # Skip if the URL for this country is not provided.

        for loc_id in ids:
            try:
                # Format the URL with the appropriate parameter.
                url = url_template.format(
                    prefecture=loc_id if country == "JP" else None,
                    country=loc_id if country == "EN" else None
                )
                response = requests.get(url)
                response.raise_for_status()
                all_stores.extend(parse_location(response.text, country))
            except requests.RequestException as e:
                print(f"Failed to fetch data for {country} with id {loc_id}: {e}")

    return all_stores


def crawl_stores() -> bool:
    """
    Crawl all game stores using their URL templates and save the results to JSON files.
    """
    for game_name, store_urls in STORES.items():
        stores_data = crawl_location(store_urls)
        output_file = f"json/{game_name}.json"
        with open(output_file, "w", encoding="utf-8") as outfile:
            json.dump(stores_data, outfile, ensure_ascii=False, indent=2)
    return True


if __name__ == "__main__":
    crawl_stores()
    dupe_stores()
