import sys
import os
import json
import numpy as np

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.connectors.landsat_raster_connector import LandsatRasterConnector

def verify_landsat():
    connector = LandsatRasterConnector()
    locations = [
        ("Ames, IA", 42.0308, -93.6319),
        ("Fresno, CA", 36.7468, -119.7726)
    ]
    
    results = {}
    for name, lat, lon in locations:
        print(f"=== VERIFYING LANDSAT FOR {name} ({lat}, {lon}) ===")
        # bypass cache to force actual network range request verification
        res = connector.fetch_field_ndvi(lat, lon, max_cloud_cover=20.0, buffer_meters=300.0, use_cache=False)
        
        print("Success:", res.get("success"))
        print("Scene ID:", res.get("scene_id"))
        print("Platform:", res.get("platform"))
        print("Acquisition Date:", res.get("acquisition_date"))
        print("Scene Cloud Cover %:", res.get("scene_cloud_cover_pct"))
        
        meta = res.get("raster_metadata", {})
        print("Red Href:", meta.get("red_band_href", "")[:80] + "...")
        print("NIR Href:", meta.get("nir_band_href", "")[:80] + "...")
        print("QA Href:", meta.get("qa_pixel_href", "")[:80] + "...")
        
        metrics = res.get("ndvi_metrics", {})
        print("Valid Pixels:", metrics.get("valid_pixel_count"), "/", metrics.get("total_window_pixels"))
        print("Valid Coverage %:", metrics.get("valid_coverage_pct"))
        print("Mean NDVI:", metrics.get("mean_ndvi"))
        print("Median NDVI:", metrics.get("median_ndvi"))
        print("Min NDVI:", metrics.get("min_ndvi"))
        print("Max NDVI:", metrics.get("max_ndvi"))
        print("IQR Range:", metrics.get("iqr_range"))
        print("Canopy Class:", metrics.get("canopy_vigor_classification"))
        print("3x3 Matrix Sample:")
        for row in res.get("sample_matrix_3x3", []):
            print("  ", row)
        print("Latency (sec):", res.get("latency_sec"))
        print("Cached:", res.get("cached"))
        print()
        results[name] = res
        
    return results

if __name__ == "__main__":
    verify_landsat()
