"""
Script: search_smap_cmr.py
Purpose: Programmatically query official NASA Earthdata CMR API to inspect and compare
         SMAP products (SPL3SMP_E, SPL3SMP, SPL4SMGP) over Athani, Erode.
Author: Senior Geospatial Data Engineer, Field Shift Project
"""

import urllib.request
import json
import os

cmr_collection_url = "https://cmr.earthdata.nasa.gov/search/collections.json"
cmr_granule_url = "https://cmr.earthdata.nasa.gov/search/granules.json"

products = [
    {"short_name": "SPL3SMP_E", "version": "006", "desc": "SMAP Enhanced L3 Radiometer Global Daily 9 km Soil Moisture"},
    {"short_name": "SPL3SMP", "version": "008", "desc": "SMAP L3 Radiometer Global Daily 36 km Soil Moisture"},
    {"short_name": "SPL4SMGP", "version": "007", "desc": "SMAP L4 Global 3-hourly 9 km Surface and Root Zone Soil Moisture"}
]

# Athani point & bounding box
point = "77.514614,11.523104"
bbox = "77.46873,11.47788,77.56050,11.56833"

print("--- Querying NASA Earthdata CMR Collections ---")
headers = {'User-Agent': 'FieldShiftBot/1.0 (NASA Space Apps Challenge; contact@fieldshift.local)'}

collection_results = {}
for prod in products:
    query = f"{cmr_collection_url}?short_name={prod['short_name']}"
    req = urllib.request.Request(query, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            entries = data.get('feed', {}).get('entry', [])
            print(f"\nProduct: {prod['short_name']} - Found {len(entries)} collection versions:")
            for e in entries:
                v = e.get('version_id')
                cid = e.get('id')
                time_start = e.get('time_start')
                time_end = e.get('time_end', 'Present')
                print(f"  Version: {v} | Concept ID: {cid} | Temporal Range: {time_start} to {time_end}")
                if v == prod['version'] or not collection_results.get(prod['short_name']):
                    collection_results[prod['short_name']] = {
                        'concept_id': cid,
                        'version': v,
                        'time_start': time_start,
                        'time_end': time_end,
                        'title': e.get('title')
                    }
    except Exception as err:
        print(f"Error querying {prod['short_name']}: {err}")

print("\n--- Querying Sample Granules over Athani Coordinates ---")
# Query 1 month (e.g., 2024-06-01 to 2024-06-30) for each selected collection
for short_name, info in collection_results.items():
    cid = info['concept_id']
    g_query = f"{cmr_granule_url}?echo_collection_id={cid}&point={point}&temporal=2024-06-01T00:00:00Z,2024-06-05T23:59:59Z&page_size=5"
    req = urllib.request.Request(g_query, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            g_data = json.loads(resp.read().decode())
            g_entries = g_data.get('feed', {}).get('entry', [])
            print(f"\nCollection {short_name} ({cid}):")
            print(f"  Granules found in 5-day window: {len(g_entries)}")
            for g in g_entries[:2]:
                title = g.get('title')
                size_mb = g.get('granule_size', 'N/A')
                links = [l.get('href') for l in g.get('links', []) if 'data#' in l.get('rel', '') or l.get('href', '').endswith(('.h5', '.nc', '.tif'))]
                print(f"  - Granule: {title} ({size_mb} MB)")
                if links:
                    print(f"    Download URL: {links[0]}")
    except Exception as err:
        print(f"Error querying granules for {short_name}: {err}")

