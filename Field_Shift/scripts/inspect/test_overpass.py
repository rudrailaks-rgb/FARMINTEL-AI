import urllib.request
import json
import urllib.parse

# Test overpass endpoint with simple query
overpass_endpoints = [
    "https://overpass.private.coffee/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass-api.de/api/interpreter"
]

query = """
[out:json][timeout:25];
(
  node(11.51, 77.50, 11.54, 77.53);
);
out count;
"""

for ep in overpass_endpoints:
    print(f"Trying {ep}...")
    try:
        data = urllib.parse.urlencode({'data': query}).encode()
        req = urllib.request.Request(ep, data=data, headers={'User-Agent': 'FieldShiftBot/1.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            res = json.loads(resp.read().decode())
            print(f"Success on {ep}: {res}")
            break
    except Exception as e:
        print(f"Error on {ep}: {e}")

