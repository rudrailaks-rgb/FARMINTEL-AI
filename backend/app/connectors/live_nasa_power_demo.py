"""
Script: live_nasa_power_demo.py
Purpose: Connect FARMINTEL AI directly to NASA POWER Daily API for Des Moines, Iowa (2025).
Parameters: T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, RH2M, ALLSKY_SFC_SW_DWN, WS10M
Location: Lat: 41.5868, Lon: -93.6250
Date range: 20250101 to 20251231
Community: AG, Format: JSON
"""

import urllib.request
import json
import os
import time
import pandas as pd

def main():
    lat = 41.5868
    lon = -93.6250
    start_date = "20250101"
    end_date = "20251231"
    params = "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN,WS10M"
    community = "AG"
    
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters={params}&community={community}&longitude={lon}&latitude={lat}&start={start_date}&end={end_date}&format=JSON"
    
    print(f"Connecting directly to official NASA POWER Daily API...")
    print(f"Endpoint: {url}\n")
    
    start_time = time.time()
    req = urllib.request.Request(url, headers={'User-Agent': 'FARMINTEL-AI/1.0 (NASA Space Apps Challenge)'})
    
    with urllib.request.urlopen(req, timeout=60) as resp:
        status_code = resp.status
        raw_bytes = resp.read()
        latency = time.time() - start_time
        data = json.loads(raw_bytes.decode('utf-8'))
        
    print(f"Connection Successful! HTTP {status_code} in {latency:.2f} seconds.")
    print(f"Downloaded payload: {len(raw_bytes):,} bytes ({len(raw_bytes)/1024:.2f} KB)")
    
    # Validation
    geom = data.get("geometry", {})
    elevation = geom.get("coordinates", [0, 0, 0])[2]
    param_dict = data.get("properties", {}).get("parameter", {})
    
    assert "T2M" in param_dict, "Validation Error: T2M missing"
    assert "PRECTOTCORR" in param_dict, "Validation Error: PRECTOTCORR missing"
    
    dates = sorted(list(param_dict["T2M"].keys()))
    print(f"Temporal coverage: {len(dates)} days (from {dates[0]} to {dates[-1]})")
    
    # Parse into DataFrame & compute statistics
    rows = []
    param_names = params.split(",")
    for d in dates:
        row = {"date": f"{d[:4]}-{d[4:6]}-{d[6:]}"}
        for p in param_names:
            val = param_dict.get(p, {}).get(d)
            row[p] = float(val) if val is not None and val > -990.0 else None
        rows.append(row)
        
    df = pd.DataFrame(rows)
    
    # Save output
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "nasa_power_demo"))
    os.makedirs(out_dir, exist_ok=True)
    
    json_path = os.path.join(out_dir, f"NASA_POWER_DesMoines_Iowa_{start_date}_{end_date}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(raw_bytes.decode('utf-8'))
        
    csv_path = os.path.join(out_dir, f"NASA_POWER_DesMoines_Iowa_{start_date}_{end_date}.csv")
    df.to_csv(csv_path, index=False)
    
    print(f"\nFiles saved locally:")
    print(f"- JSON: {json_path}")
    print(f"- CSV:  {csv_path}")
    
    print("\n--- STATISTICAL ANALYSIS (365 DAYS) ---")
    for p in param_names:
        s = df[p]
        print(f"{p:18s} | Mean: {s.mean():7.2f} | Min: {s.min():7.2f} | Max: {s.max():7.2f} | Std: {s.std():6.2f} | Missing: {s.isna().sum()}")

if __name__ == "__main__":
    main()
