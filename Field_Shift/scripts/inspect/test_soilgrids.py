import urllib.request
import json

url = "https://rest.isric.org/soilgrids/v2.0/properties/query?lon=77.514614&lat=11.523104&property=phh2o&property=soc&property=sand&property=silt&property=clay&property=bdod&property=cec&property=nitrogen&depth=0-5cm&depth=5-15cm&depth=15-30cm&depth=30-60cm&depth=60-100cm&depth=100-200cm&value=mean&value=uncertainty"
req = urllib.request.Request(url, headers={'User-Agent': 'FieldShiftBot/1.0'})
try:
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode())
        layers = data.get('properties', {}).get('layers', [])
        print(f"SoilGrids query succeeded! Layers returned: {len(layers)}")
        for l in layers:
            print(f"- {l.get('name')}: {l.get('unit_measure', {}).get('target_units')}")
except Exception as e:
    print("SoilGrids Error:", e)

