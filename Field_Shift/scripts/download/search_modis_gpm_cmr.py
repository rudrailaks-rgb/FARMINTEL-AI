"""
Script: search_modis_gpm_cmr.py
Purpose: Query NASA Earthdata CMR API for MODIS MOD13Q1 (Tile h25v07) and GPM IMERG Final Run.
Author: Senior Geospatial Data Engineer, Field Shift Project
"""

import urllib.request
import json

cmr_granule_url = "https://cmr.earthdata.nasa.gov/search/granules.json"
point = "77.514614,11.523104"
headers = {'User-Agent': 'FieldShiftBot/1.0'}

print("--- 1. Querying MODIS MOD13Q1 v061 (Tile h25v07) ---")
modis_query = f"{cmr_granule_url}?short_name=MOD13Q1&version=061&point={point}&temporal=2024-01-01T00:00:00Z,2024-03-31T23:59:59Z&page_size=5"
try:
    req = urllib.request.Request(modis_query, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
        entries = data.get('feed', {}).get('entry', [])
        print(f"MOD13Q1 granules found in sample window: {len(entries)}")
        for e in entries[:2]:
            title = e.get('title')
            size_mb = e.get('granule_size', 'N/A')
            links = [l.get('href') for l in e.get('links', []) if 'data#' in l.get('rel', '') or l.get('href', '').endswith(('.hdf', '.tif'))]
            print(f"  Granule: {title} ({size_mb} MB)")
            if links:
                print(f"  Direct Link: {links[0]}")
except Exception as err:
    print("MODIS CMR error:", err)

print("\n--- 2. Querying GPM IMERG Final Run (GPM_3IMERGDF v07) ---")
gpm_query = f"{cmr_granule_url}?short_name=GPM_3IMERGDF&version=07&point={point}&temporal=2024-06-01T00:00:00Z,2024-06-05T23:59:59Z&page_size=5"
try:
    req = urllib.request.Request(gpm_query, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
        entries = data.get('feed', {}).get('entry', [])
        print(f"GPM IMERG granules found in sample window: {len(entries)}")
        for e in entries[:2]:
            title = e.get('title')
            size_mb = e.get('granule_size', 'N/A')
            links = [l.get('href') for l in e.get('links', []) if 'data#' in l.get('rel', '') or l.get('href', '').endswith(('.nc4', '.hdf5', '.tif'))]
            print(f"  Granule: {title} ({size_mb} MB)")
            if links:
                print(f"  Direct Link: {links[0]}")
except Exception as err:
    print("GPM CMR error:", err)

