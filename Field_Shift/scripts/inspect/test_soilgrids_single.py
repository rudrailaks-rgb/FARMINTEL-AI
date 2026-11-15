import urllib.request
import json

url = "https://rest.isric.org/soilgrids/v2.0/properties/query?lon=77.514614&lat=11.523104&property=phh2o&depth=0-5cm&value=mean"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    print(f"Querying: {url}")
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode())
        print("Success! Response:")
        print(json.dumps(data, indent=2))
except Exception as e:
    print("Error:", e)

