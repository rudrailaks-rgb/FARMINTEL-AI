"""
Script: download_nasa_power.py
Purpose: Download official NASA POWER daily agroclimatology data (2015-01-01 to 2025-12-31)
         for Athani, Erode (Lat: 11.523104, Lon: 77.514614).
Author: Senior Geospatial Data Engineer, Field Shift Project
"""

import urllib.request
import os
import sys
import time

def download_file(url, output_path):
    print(f"Initiating download from:\n  {url}")
    print(f"Target destination:\n  {output_path}")
    req = urllib.request.Request(url, headers={'User-Agent': 'FieldShiftBot/1.0 (NASA Space Apps Challenge; contact@fieldshift.local)'})
    start_time = time.time()
    with urllib.request.urlopen(req, timeout=120) as resp:
        content = resp.read()
        with open(output_path, "wb") as f:
            f.write(content)
    elapsed = time.time() - start_time
    file_size_kb = os.path.getsize(output_path) / 1024
    print(f"Download complete: {file_size_kb:.2f} KB written in {elapsed:.2f} seconds.")
    return output_path

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    raw_dir = os.path.join(base_dir, "data", "raw", "nasa_power")
    os.makedirs(raw_dir, exist_ok=True)
    
    lat = 11.523104
    lon = 77.514614
    start_date = "20150101"
    end_date = "20251231"
    params = "PRECTOTCORR,T2M,T2M_MAX,T2M_MIN,RH2M,ALLSKY_SFC_SW_DWN"
    community = "AG"
    
    # 1. Download official CSV product
    csv_filename = f"NASA_POWER_Daily_Agroclimatology_Athani_Erode_{start_date}_{end_date}.csv"
    csv_path = os.path.join(raw_dir, csv_filename)
    csv_url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters={params}&community={community}&longitude={lon}&latitude={lat}&start={start_date}&end={end_date}&format=CSV"
    
    download_file(csv_url, csv_path)
    
    # 2. Also download JSON formatted metadata & payload to ensure zero ambiguity in units and attributes
    json_filename = f"NASA_POWER_Daily_Agroclimatology_Athani_Erode_{start_date}_{end_date}.json"
    json_path = os.path.join(raw_dir, json_filename)
    json_url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters={params}&community={community}&longitude={lon}&latitude={lat}&start={start_date}&end={end_date}&format=JSON"
    
    download_file(json_url, json_path)
    
    print("\nNASA POWER acquisition completed successfully.")

if __name__ == "__main__":
    main()

