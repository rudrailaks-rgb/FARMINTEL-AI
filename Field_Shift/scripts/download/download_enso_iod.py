"""
Script: download_enso_iod.py
Purpose: Download and process official NOAA ENSO and IOD teleconnection climate indices.
Author: Senior Geospatial Data Engineer, Field Shift Project
"""

import urllib.request
import os
import pandas as pd
import json

def download_enso_iod():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    raw_dir = os.path.join(base_dir, "data", "raw", "enso_iod")
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(raw_dir, exist_ok=True)
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) FieldShiftBot/1.0'}
    
    # 1. Download NOAA ONI (Oceanic Niño Index)
    oni_url = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
    oni_raw_file = os.path.join(raw_dir, "NOAA_CPC_ONI_Index.txt")
    print(f"Downloading ONI from {oni_url}...")
    req = urllib.request.Request(oni_url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read()
        with open(oni_raw_file, "wb") as f:
            f.write(content)
    print(f"ONI saved: {oni_raw_file} ({len(content)} bytes)")
    
    # 2. Download NOAA Niño 3.4 monthly anomalies
    nino_url = "https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.81-10.ascii"
    nino_raw_file = os.path.join(raw_dir, "NOAA_CPC_NINO_Regions_Monthly.txt")
    print(f"Downloading Niño 3.4 from {nino_url}...")
    req = urllib.request.Request(nino_url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read()
        with open(nino_raw_file, "wb") as f:
            f.write(content)
    print(f"Niño regions saved: {nino_raw_file} ({len(content)} bytes)")
    
    # 3. Download HadISST DMI (Dipole Mode Index for IOD)
    dmi_url = "https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/dmi.had.long.data"
    dmi_raw_file = os.path.join(raw_dir, "HadISST_DMI_Indian_Ocean_Dipole.txt")
    print(f"Downloading DMI from {dmi_url}...")
    req = urllib.request.Request(dmi_url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read()
        with open(dmi_raw_file, "wb") as f:
            f.write(content)
    print(f"DMI saved: {dmi_raw_file} ({len(content)} bytes)")
    
    # Parse ONI: columns SEAS, YR, TOTAL, ANOM
    oni_df = pd.read_csv(oni_raw_file, sep=r'\s+')
    oni_filtered = oni_df[(oni_df['YR'] >= 2015) & (oni_df['YR'] <= 2025)].copy()
    
    # Parse Niño 3.4
    with open(nino_raw_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    data_rows = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 10:
            try:
                yr = int(parts[0])
                mon = int(parts[1])
                nino34_anom = float(parts[9])
                nino34_total = float(parts[8])
                data_rows.append({
                    'Year': yr,
                    'Month': mon,
                    'Nino34_Total_SST': nino34_total,
                    'Nino34_Anomaly': nino34_anom,
                    'ENSO_Phase': 'El Niño' if nino34_anom >= 0.5 else ('La Niña' if nino34_anom <= -0.5 else 'Neutral')
                })
            except ValueError:
                continue
    nino_df = pd.DataFrame(data_rows)
    nino_filtered = nino_df[(nino_df['Year'] >= 2015) & (nino_df['Year'] <= 2025)].copy()
    
    # Save processed unified climate index CSV
    unified_csv = os.path.join(raw_dir, "ENSO_Nino34_Monthly_2015_2025.csv")
    nino_filtered.to_csv(unified_csv, index=False)
    print(f"Unified climate indices saved to: {unified_csv} ({len(nino_filtered)} monthly records)")
    
    return unified_csv

if __name__ == "__main__":
    download_enso_iod()
