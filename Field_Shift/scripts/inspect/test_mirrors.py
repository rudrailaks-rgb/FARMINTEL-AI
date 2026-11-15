import json
import urllib.request
import urllib.parse

mirrors = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
]

query = """
[out:json][timeout:30];
(
  node(around:3000, 11.523104, 77.514614)["amenity"];
  node(around:3000, 11.523104, 77.514614)["place"];
  way(around:3000, 11.523104, 77.514614)["landuse"];
  way(around:3000, 11.523104, 77.514614)["boundary"];
  relation(around:5000, 11.523104, 77.514614)["boundary"="administrative"];
);
out tags center;
"""

headers = {'User-Agent': 'FieldShiftResearchBot/1.0 (NASA Space Apps Challenge; contact@fieldshift.local)'}

for endpoint in mirrors:
    print(f"Trying endpoint: {endpoint}")
    try:
        req = urllib.request.Request(endpoint, data=urllib.parse.urlencode({'data': query}).encode(), headers=headers)
        with urllib.request.urlopen(req, timeout=35) as resp:
            data = json.loads(resp.read().decode())
            elements = data.get('elements', [])
            print(f"Success! Elements found: {len(elements)}")
            for el in elements:
                t = el.get('tags', {})
                print(f"- Type: {el.get('type')}, ID: {el.get('id')}, Name: {t.get('name')}, Amenity: {t.get('amenity')}, Place: {t.get('place')}, Landuse: {t.get('landuse')}, Boundary: {t.get('boundary')}")
            break
    except Exception as e:
        print(f"Failed with {endpoint}: {e}")

