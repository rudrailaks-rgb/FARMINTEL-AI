import urllib.request
import json

headers = {'User-Agent': 'FieldShiftResearchBot/1.0 (contact@fieldshift.local)'}

# Search Nominatim for osm_type and osm_id of Athani, Erode
url = "https://nominatim.openstreetmap.org/search?q=Athani,+Anthiyur,+Erode&format=json&extratags=1&addressdetails=1"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        print("Search Athani, Anthiyur, Erode:")
        for r in res:
            print("Name:", r.get('display_name'))
            print("OSM Type:", r.get('osm_type'), "OSM ID:", r.get('osm_id'))
            print("Lat/Lon:", r.get('lat'), r.get('lon'))
            print("BBox:", r.get('boundingbox'))
            print("Extratags:", r.get('extratags'))
except Exception as e:
    print("Error:", e)

