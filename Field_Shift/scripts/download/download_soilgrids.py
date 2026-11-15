"""
Script: download_soilgrids.py
Purpose: Download official ISRIC SoilGrids 2.0 properties for Athani, Erode (Lat: 11.523104, Lon: 77.514614).
         Properties: phh2o, soc, nitrogen, sand, silt, clay, bdod, cec.
         Depths: 0-5cm, 5-15cm, 15-30cm, 30-60cm, 60-100cm, 100-200cm.
         Values: Mean and Quantile Uncertainty (Q0.05, Q0.5, Q0.95).
Author: Senior Geospatial Data Engineer, Field Shift Project
"""

import urllib.request
import json
import os
import time
import pandas as pd

def download_soilgrids():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    raw_dir = os.path.join(base_dir, "data", "raw", "soilgrids")
    os.makedirs(raw_dir, exist_ok=True)
    
    lat = 11.523104
    lon = 77.514614
    
    properties = ["phh2o", "soc", "nitrogen", "sand", "silt", "clay", "bdod", "cec"]
    depths = ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"]
    
    depth_query = "&".join([f"depth={d}" for d in depths])
    
    headers = {'User-Agent': 'FieldShiftBot/1.0 (NASA Space Apps Challenge; contact@fieldshift.local)'}
    
    all_results = {}
    rows = []
    
    print(f"Connecting to official ISRIC SoilGrids REST API for Athani ({lat}, {lon})...")
    
    for prop in properties:
        url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property={prop}&{depth_query}&value=mean&value=uncertainty"
        print(f"Fetching property '{prop}'...")
        req = urllib.request.Request(url, headers=headers)
        success = False
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode())
                    all_results[prop] = data
                    
                    layers = data.get('properties', {}).get('layers', [])
                    for layer in layers:
                        unit_info = layer.get('unit_measure', {})
                        d_factor = unit_info.get('d_factor', 1)
                        target_units = unit_info.get('target_units', '')
                        mapped_units = unit_info.get('mapped_units', '')
                        
                        for d in layer.get('depths', []):
                            depth_label = d.get('label')
                            top_depth = d.get('range', {}).get('top_depth')
                            bottom_depth = d.get('range', {}).get('bottom_depth')
                            vals = d.get('values', {})
                            
                            mean_raw = vals.get('mean')
                            mean_scaled = round(mean_raw / d_factor, 3) if mean_raw is not None else None
                            
                            q05_raw = vals.get('Q0.05')
                            q05_scaled = round(q05_raw / d_factor, 3) if q05_raw is not None else None
                            
                            q50_raw = vals.get('Q0.5')
                            q50_scaled = round(q50_raw / d_factor, 3) if q50_raw is not None else None
                            
                            q95_raw = vals.get('Q0.95')
                            q95_scaled = round(q95_raw / d_factor, 3) if q95_raw is not None else None
                            
                            rows.append({
                                'Location': 'Athani, Erode',
                                'Latitude': lat,
                                'Longitude': lon,
                                'Property_Code': prop,
                                'Depth_Label': depth_label,
                                'Top_Depth_cm': top_depth,
                                'Bottom_Depth_cm': bottom_depth,
                                'Raw_Mean': mean_raw,
                                'Scaled_Mean': mean_scaled,
                                'Q0.05_Uncertainty': q05_scaled,
                                'Q0.50_Median': q50_scaled,
                                'Q0.95_Uncertainty': q95_scaled,
                                'Unit': target_units,
                                'Mapped_Unit': mapped_units,
                                'Scale_Factor': d_factor
                            })
                    success = True
                    break
            except Exception as e:
                print(f"  Attempt {attempt+1} failed for {prop}: {e}. Retrying...")
                time.sleep(2)
        if not success:
            print(f"  Failed to retrieve property: {prop}")
            
    # Save complete raw JSON response
    json_path = os.path.join(raw_dir, "SoilGrids_Properties_Athani_Erode.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nRaw JSON saved to: {json_path} ({os.path.getsize(json_path)/1024:.2f} KB)")
    
    # Save structured tabular CSV
    df = pd.DataFrame(rows)
    csv_path = os.path.join(raw_dir, "SoilGrids_Properties_Athani_Erode.csv")
    df.to_csv(csv_path, index=False)
    print(f"Structured CSV saved to: {csv_path} ({os.path.getsize(csv_path)/1024:.2f} KB, {len(df)} rows)")
    
    return json_path, csv_path

if __name__ == "__main__":
    download_soilgrids()

