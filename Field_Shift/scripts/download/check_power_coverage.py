import urllib.request
import json

base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
params = {
    "parameters": "PRECTOTCORR,T2M",
    "community": "AG",
    "longitude": "77.514614",
    "latitude": "11.523104",
    "start": "20251201",
    "end": "20251231",
    "format": "JSON"
}

query_str = "&".join([f"{k}={v}" for k, v in params.items()])
full_url = f"{base_url}?{query_str}"
req = urllib.request.Request(full_url, headers={'User-Agent': 'FieldShiftBot/1.0'})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
        dates = list(data.get('properties', {}).get('parameter', {}).get('T2M', {}).keys())
        print(f"2025-12 query succeeded: {len(dates)} dates returned: {dates[0]} to {dates[-1]}")
except Exception as e:
    print("Error:", e)

