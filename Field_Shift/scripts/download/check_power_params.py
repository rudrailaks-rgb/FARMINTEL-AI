import urllib.request
import json

url = "https://power.larc.nasa.gov/api/system/manager/parameters"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'FieldShiftBot/1.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        precip_params = [k for k in data.keys() if 'PREC' in k]
        print("Precipitation parameters found in NASA POWER:")
        for p in precip_params:
            print(f"- {p}: {data[p].get('longname')} (Units: {data[p].get('units')})")
except Exception as e:
    print("Error:", e)

