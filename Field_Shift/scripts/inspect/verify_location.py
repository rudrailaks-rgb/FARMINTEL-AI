import json
import urllib.request
import urllib.parse
import time

headers = {'User-Agent': 'FieldShiftResearchBot/1.0 (NASA Space Apps Challenge; contact@fieldshift.local)'}

# 1. Reverse geocode provisional coordinates
lat, lon = 11.523104418, 77.514614464
print(f"--- 1. Testing Provisional Coordinates: Lat {lat}, Lon {lon} ---")
rev_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&zoom=18"
req = urllib.request.Request(rev_url, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print("Reverse Geocode Result:")
        print(f"Display Name: {data.get('display_name')}")
        print(f"Address breakdown: {json.dumps(data.get('address'), indent=2)}")
        print(f"OSM Type: {data.get('osm_type')}, OSM ID: {data.get('osm_id')}")
        print(f"Bounding Box: {data.get('boundingbox')}")
except Exception as e:
    print("Reverse geocoding error:", e)

time.sleep(1.5)

# 2. Search for Athani, Erode specifically
print("\n--- 2. Searching for 'Athani, Erode, Tamil Nadu' ---")
query = "Athani, Erode, Tamil Nadu"
search_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&polygon_geojson=1"
req2 = urllib.request.Request(search_url, headers=headers)
try:
    with urllib.request.urlopen(req2) as resp:
        search_data = json.loads(resp.read().decode())
        print(f"Found {len(search_data)} results:")
        for idx, item in enumerate(search_data):
            print(f"Result {idx+1}:")
            print(f"  Name: {item.get('display_name')}")
            print(f"  Class: {item.get('class')}, Type: {item.get('type')}")
            print(f"  Lat: {item.get('lat')}, Lon: {item.get('lon')}")
            print(f"  Bounding Box: {item.get('boundingbox')}")
            if 'geojson' in item:
                print(f"  GeoJSON Type: {item['geojson'].get('type')}")
except Exception as e:
    print("Search error:", e)

time.sleep(1.5)

# 3. Search for Maharishi Vidya Mandir, Athani
print("\n--- 3. Searching for 'Maharishi Vidya Mandir, Athani' ---")
query3 = "Maharishi Vidya Mandir, Athani"
search_url3 = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query3)}&format=json"
req3 = urllib.request.Request(search_url3, headers=headers)
try:
    with urllib.request.urlopen(req3) as resp:
        mvm_data = json.loads(resp.read().decode())
        print(f"MVM Results: {len(mvm_data)}")
        for idx, item in enumerate(mvm_data):
            print(f"  Name: {item.get('display_name')}, Lat: {item.get('lat')}, Lon: {item.get('lon')}")
except Exception as e:
    print("MVM search error:", e)

time.sleep(1.5)

# 4. Check other Athani locations in India to establish distinctions
print("\n--- 4. Checking disambiguation: Other 'Athani' in India ---")
query4 = "Athani, India"
search_url4 = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query4)}&format=json"
req4 = urllib.request.Request(search_url4, headers=headers)
try:
    with urllib.request.urlopen(req4) as resp:
        other_athani = json.loads(resp.read().decode())
        print(f"All 'Athani' in India results ({len(other_athani)}):")
        for idx, item in enumerate(other_athani):
            print(f"  {idx+1}: {item.get('display_name')} (Lat: {item.get('lat')}, Lon: {item.get('lon')})")
except Exception as e:
    print("Disambiguation search error:", e)

