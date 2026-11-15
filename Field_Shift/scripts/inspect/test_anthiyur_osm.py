import urllib.request
import json
import urllib.parse

# Test query for Anthiyur / Athani relations
query = """
[out:json][timeout:20];
area["name"="Anthiyur"]->.a;
(
  relation["admin_level"](area.a);
  relation["boundary"="administrative"](11.48, 77.48, 11.56, 77.56);
);
out tags;
"""

url = "https://overpass-api.de/api/interpreter"
req = urllib.request.Request(url, data=urllib.parse.urlencode({'data': query}).encode(), headers={'User-Agent': 'FieldShiftBot/1.0'})
try:
    with urllib.request.urlopen(req, timeout=25) as resp:
        res = json.loads(resp.read().decode())
        print("Overpass result:", res.get('elements'))
except Exception as e:
    print("Overpass error:", e)

