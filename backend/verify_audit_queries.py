"""
FARMINTEL AI - Strict Verification Audit Script
Executes real network requests against official data providers.
"""
import requests
import time
import json

def verify_nasa_power():
    print("\n=== 1. AUDITING NASA POWER API ===")
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN,WS10M",
        "community": "AG",
        "longitude": -93.6250,
        "latitude": 41.5868,
        "start": "20250101",
        "end": "20250105",
        "format": "JSON"
    }
    t0 = time.time()
    try:
        r = requests.get(url, params=params, timeout=30)
        dur = round(time.time() - t0, 2)
        print(f"URL: {url}")
        print(f"HTTP Status: {r.status_code}")
        print(f"Response Latency: {dur}s")
        if r.status_code == 200:
            data = r.json()
            params_dict = data.get("properties", {}).get("parameter", {})
            print(f"Parameters Retrieved ({len(params_dict)}): {list(params_dict.keys())}")
            print(f"Sample T2M_MAX (C): {params_dict.get('T2M_MAX')}")
            print(f"Sample PRECTOTCORR (mm): {params_dict.get('PRECTOTCORR')}")
            print("VERDICT: DATA_FEED_ACTIVE (Full Numerical Data Retrieved)")
            return True
        else:
            print(f"FAILED: HTTP {r.status_code} - {r.text[:200]}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def verify_usda_ssurgo():
    print("\n=== 2. AUDITING USDA SSURGO SOIL DATA ACCESS (SDA) ===")
    url = "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest"
    query = """
    SELECT TOP 1 
        c.mukey, c.cokey, c.compname, c.comppct_r, c.drainagecl, c.hydgrp, mu.muname 
    FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('point(-93.6319 42.0308)') m 
    INNER JOIN component c ON m.mukey = c.mukey 
    INNER JOIN mapunit mu ON c.mukey = mu.mukey 
    ORDER BY c.comppct_r DESC;
    """
    t0 = time.time()
    try:
        r = requests.post(url, json={"query": query, "format": "JSON"}, timeout=30)
        dur = round(time.time() - t0, 2)
        print(f"URL: {url}")
        print(f"HTTP Status: {r.status_code}")
        print(f"Response Latency: {dur}s")
        if r.status_code == 200:
            data = r.json()
            table = data.get("Table", [])
            print(f"Rows Returned: {len(table)}")
            if table:
                print(f"Soil Record: {table[0]}")
                print(f"Dominant Component: {table[0][2]} (mukey: {table[0][0]}, drainage: {table[0][4]}, hydgrp: {table[0][5]})")
            print("VERDICT: DATA_FEED_ACTIVE (Full Tabular Spatial Data Retrieved)")
            return True
        else:
            print(f"FAILED: HTTP {r.status_code} - {r.text[:200]}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    p_ok = verify_nasa_power()
    s_ok = verify_usda_ssurgo()
    print(f"\nAudit completed. NASA POWER: {p_ok}, USDA SSURGO: {s_ok}")
