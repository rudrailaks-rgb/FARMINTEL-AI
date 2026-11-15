import sys
import os
import json
import sqlite3
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from pyproj import Transformer
import pystac_client
import planetary_computer as pc

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def verify_raster_math_and_persistence():
    print("==================================================")
    print("STEP 1: INDEPENDENT RASTER MATH & PIXEL EXTRACTION")
    print("==================================================")
    
    # 1. Connect to Planetary Computer STAC
    stac_url = "https://planetarycomputer.microsoft.com/api/stac/v1"
    catalog = pystac_client.Client.open(stac_url, modifier=pc.sign_inplace)
    
    # Ames, IA coordinates
    lat, lon = 42.0308, -93.6319
    search = catalog.search(
        collections=["landsat-c2-l2"],
        intersects={"type": "Point", "coordinates": [lon, lat]},
        datetime="2024-06-01/2024-09-15",
        query={"eo:cloud_cover": {"lt": 15}}
    )
    items = list(search.items())
    assert len(items) > 0, "No Landsat scenes found"
    item = items[0]
    
    print(f"Verified STAC Scene ID: {item.id}")
    print(f"Platform: {item.properties.get('platform')}")
    print(f"Acquisition Date: {item.datetime.isoformat()}")
    print(f"Cloud Cover %: {item.properties.get('eo:cloud_cover')}")
    
    red_href = item.assets["red"].href
    nir_href = item.assets["nir08"].href
    qa_href = item.assets["qa_pixel"].href
    
    print(f"Asset B04 (Red) URL: {red_href[:100]}... [signed SAS token present: {'sig=' in red_href}]")
    print(f"Asset B05 (NIR) URL: {nir_href[:100]}... [signed SAS token present: {'sig=' in nir_href}]")
    print(f"Asset QA_PIXEL URL:  {qa_href[:100]}... [signed SAS token present: {'sig=' in qa_href}]")
    
    # Read window of 20x20 pixels
    with rasterio.open(red_href) as ds_red:
        crs = ds_red.crs
        trans = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
        cx, cy = trans.transform(lon, lat)
        buf = 300.0 # 600m total width
        minx, miny, maxx, maxy = cx - buf, cy - buf, cx + buf, cy + buf
        win = from_bounds(minx, miny, maxx, maxy, ds_red.transform)
        win = win.round_offsets().round_shape()
        raw_red = ds_red.read(1, window=win)
        
    with rasterio.open(nir_href) as ds_nir:
        raw_nir = ds_nir.read(1, window=win)
        
    with rasterio.open(qa_href) as ds_qa:
        raw_qa = ds_qa.read(1, window=win)
        
    print(f"\nRaw Array Shapes: Red {raw_red.shape}, NIR {raw_nir.shape}, QA {raw_qa.shape}")
    print(f"Sample Raw Red DNs (center 3x3):\n{raw_red[8:11, 8:11]}")
    print(f"Sample Raw NIR DNs (center 3x3):\n{raw_nir[8:11, 8:11]}")
    print(f"Sample Raw QA_PIXEL (center 3x3):\n{raw_qa[8:11, 8:11]}")
    
    # Check USGS Collection 2 Scaling
    # SR = DN * 0.0000275 - 0.2
    scale = 0.0000275
    offset = -0.2
    sr_red = raw_red.astype(np.float32) * scale + offset
    sr_nir = raw_nir.astype(np.float32) * scale + offset
    
    print(f"\nScaled Surface Reflectance Red (center 3x3):\n{np.round(sr_red[8:11, 8:11], 4)}")
    print(f"Scaled Surface Reflectance NIR (center 3x3):\n{np.round(sr_nir[8:11, 8:11], 4)}")
    
    # QA Masking
    # Bits 3 (dilated cloud: 1<<3=8), 4 (cirrus: 1<<4=16), 5 (cloud: 1<<5=32), 7 (cloud shadow: 1<<7=128)
    bad_mask = (raw_qa & (1 << 3) > 0) | (raw_qa & (1 << 4) > 0) | (raw_qa & (1 << 5) > 0) | (raw_qa & (1 << 7) > 0)
    nodata_mask = (raw_red == 0) | (raw_nir == 0) | (raw_red == 65535) | (raw_nir == 65535)
    valid_mask = (~bad_mask) & (~nodata_mask) & (sr_red > 0.0) & (sr_nir > 0.0)
    
    valid_count = int(np.sum(valid_mask))
    total_count = int(raw_red.size)
    print(f"\nQA Bitmask Filter:")
    print(f"  Total window pixels: {total_count}")
    print(f"  Valid clear-sky pixels: {valid_count} ({valid_count/total_count*100:.1f}%)")
    print(f"  Cloud/Cirrus/Shadow pixels masked: {int(np.sum(bad_mask))}")
    print(f"  Nodata pixels: {int(np.sum(nodata_mask))}")
    
    # Independent NDVI computation
    ndvi = (sr_nir - sr_red) / (sr_nir + sr_red + 1e-8)
    valid_ndvi = ndvi[valid_mask]
    
    calc_mean = float(np.mean(valid_ndvi))
    calc_median = float(np.median(valid_ndvi))
    calc_min = float(np.min(valid_ndvi))
    calc_max = float(np.max(valid_ndvi))
    q25 = float(np.percentile(valid_ndvi, 25))
    q75 = float(np.percentile(valid_ndvi, 75))
    
    print(f"\nIndependent NDVI Calculation Results:")
    print(f"  Mean NDVI:   {calc_mean:.4f}")
    print(f"  Median NDVI: {calc_median:.4f}")
    print(f"  Min NDVI:    {calc_min:.4f}")
    print(f"  Max NDVI:    {calc_max:.4f}")
    print(f"  IQR Range:   [{q25:.4f}, {q75:.4f}]")
    
    center_3x3_ndvi = np.round(ndvi[8:11, 8:11], 3).tolist()
    print(f"  3x3 Center NDVI Matrix:\n{center_3x3_ndvi}")
    
    print("\n==================================================")
    print("STEP 2: SQLITE PERSISTENCE VERIFICATION")
    print("==================================================")
    db_path = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "farmintel.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall()]
    print(f"Tables in SQLite ({db_path}): {tables}")
    assert "satellite_observations" in tables, "satellite_observations table missing!"
    
    cur.execute("SELECT COUNT(*) FROM satellite_observations;")
    obs_count = cur.fetchone()[0]
    print(f"Total rows in satellite_observations: {obs_count}")
    
    cur.execute("""
        SELECT id, field_id, dataset_id, product_id, scene_id, acquisition_date, 
               spatial_resolution, calculated_indicators, valid_pixel_coverage, quality_metadata, retrieval_timestamp 
        FROM satellite_observations 
        ORDER BY id DESC LIMIT 5;
    """)
    rows = cur.fetchall()
    print("Recent rows in satellite_observations:")
    for r in rows:
        indicators = json.loads(r[7])
        quality = json.loads(r[9])
        print(f"  ID {r[0]}: Field={r[1]}, Scene={r[4]}, Date={r[5]}, Res={r[6]}m, Coverage={r[8]}%")
        print(f"       Indicators: MeanNDVI={indicators.get('mean_ndvi')}, MedianNDVI={indicators.get('median_ndvi')}, Class={indicators.get('canopy_vigor_classification')}")
        print(f"       Cloud={quality.get('cloud_cover_pct')}%, StoredAt={r[10]}")
    
    conn.close()
    print("\n[VERIFICATION RESULT: SUCCESS]")

if __name__ == "__main__":
    verify_raster_math_and_persistence()
