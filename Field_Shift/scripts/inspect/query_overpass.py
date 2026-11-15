import json
import urllib.request
import urllib.parse

headers = {'User-Agent': 'FieldShiftResearchBot/1.0 (NASA Space Apps Challenge; contact@fieldshift.local)'}

overpass_url = "https://overpass-api.de/api/interpreter"

# Query 1: Find any relation or way with name containing Athani in Erode area
query = """
[out:json][timeout:25];
(
  relation["name"~"Athani",i](11.45, 77.45, 11.60, 77.58);
  relation["admin_level"](11.50, 77.49, 11.55, 77.54);
  way["name"~"Athani",i]["boundary"="administrative"](11.45, 77.45, 11.60, 77.58);
  node["place"](11.50, 77.49, 11.55, 77.54);
);
out body;
>;
out skel qt;
"""

print("Executing Overpass query...")
req = urllib.request.Request(overpass_url, data=urllib.parse.urlencode({'data': query}).encode(), headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        elements = res.get('elements', [])
        print(f"Total elements returned: {len(elements)}")
        for el in elements:
            if el.get('type') in ['relation', 'node', 'way'] and 'tags' in el:
                tags = el['tags']
                if 'name' in tags or 'boundary' in tags or 'place' in tags:
                    print(f"Type: {el.get('type')}, ID: {el.get('id')}, Name: {tags.get('name')}, Name:ta: {tags.get('name:ta')}, Place: {tags.get('place')}, Boundary: {tags.get('boundary')}, Admin Level: {tags.get('admin_level')}")
except Exception as e:
    print("Overpass error:", e)

