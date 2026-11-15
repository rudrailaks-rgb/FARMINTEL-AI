"""
Script: test_nasa_power_api.py
Purpose: Test the official NASA POWER Daily Agroclimatology Point API for Athani coordinates.
"""

import urllib.request
import json

base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
params = {
    "parameters": "PRECTOTCORR,T2M,T2M_MAX,T2M_MIN,RH2M,ALLSKY_SFC_SW_DWN",
    "community": "AG",
    "longitude": "77.514614",
    "latitude": "11.523104",
    "start": "20250101", # test 1-month request first to verify response structure
    "end": "20250131",
    "format": "JSON"
}

query_str = "&".join([f"{k}={v}" for k, v in params.items()])
full_url = f"{base_url}?{query_str}"

print(f"Testing URL: {full_url}")
req = urllib.request.Request(full_url, headers={'User-Agent': 'FieldShiftBot/1.0'})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
        print("API Response Header:", list(data.keys()))
        print("Messages:", data.get('messages'))
        print("Parameters returned:", list(data.get('properties', {}).get('parameter', {}).keys()))
        dates = list(data.get('properties', {}).get('parameter', {}).get('T2M', {}).keys())
        print(f"Dates returned: {len(dates)} days (First: {dates[0]}, Last: {dates[-1]})")
        print("Sample T2M:", {d: data['properties']['parameter']['T2M'][d] for d in dates[:3]})
except Exception as e:
    print("API Error:", e)

