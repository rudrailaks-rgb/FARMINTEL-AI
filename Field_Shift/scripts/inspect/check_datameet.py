import urllib.request
import json

headers = {'User-Agent': 'FieldShiftBot/1.0'}

# Search GitHub repo for Erode / Athani / 803514
urls_to_try = [
    "https://raw.githubusercontent.com/datameet/Municipal_Spatial_Data/master/TamilNadu/TownPanchayats.geojson",
    "https://raw.githubusercontent.com/datameet/indian_village_boundaries/master/tamil_nadu/erode.geojson"
]

for url in urls_to_try:
    print(f"Checking URL: {url}")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"Status: {resp.status}, Content-Length: {resp.headers.get('Content-Length')}")
    except Exception as e:
        print(f"Error: {e}")

