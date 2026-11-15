import sys
import os
import json
import requests
import sqlite3

def verify_live_api_3_locations():
    print("==================================================")
    print("STEP 3: LIVE API MULTI-LOCATION AUDIT")
    print("==================================================")
    
    locations = [
        {
            "id": "loc_ames_ia",
            "name": "Story County Experimental Plot (Ames, IA)",
            "latitude": 42.0308,
            "longitude": -93.6319,
            "region_name": "Midwest Corn Belt"
        },
        {
            "id": "loc_fresno_ca",
            "name": "San Joaquin Valley Plot (Fresno, CA)",
            "latitude": 36.7468,
            "longitude": -119.7726,
            "region_name": "California Central Valley"
        },
        {
            "id": "loc_finney_ks",
            "name": "High Plains Research Farm (Finney County, KS)",
            "latitude": 37.9717,
            "longitude": -100.8654,
            "region_name": "Great Plains Winter Wheat Belt"
        }
    ]
    
    api_url = "http://127.0.0.1:8000/api/field/analyze"
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "data", "farmintel.db"))
    
    audit_results = {}
    
    for loc in locations:
        print(f"\n========================================================")
        print(f"CALLING LIVE API FOR: {loc['name']}")
        print(f"Coordinates: ({loc['latitude']}, {loc['longitude']}) | Region: {loc['region_name']}")
        print(f"========================================================")
        
        payload = {
            "field_id": loc["id"],
            "field_name": loc["name"],
            "latitude": loc["latitude"],
            "longitude": loc["longitude"],
            "total_area_acres": 160.0
        }
        
        try:
            resp = requests.post(api_url, json=payload, timeout=90)
            print(f"HTTP Status: {resp.status_code}")
            assert resp.status_code == 200, f"API returned non-200: {resp.status_code} - {resp.text}"
            data = resp.json()
            
            # 1. Geospatial Context
            geo = data.get("geospatial_context", {})
            print("\n1. GEOSPATIAL CONTEXT:")
            print(f"   Country: {geo.get('country')}, State: {geo.get('state')}, County: {geo.get('county')}")
            print(f"   Geospatial Hash: {geo.get('geospatial_hash')}")
            print(f"   Successful Sources: {geo.get('successful_sources')}")
            print(f"   Analysis Timestamp: {geo.get('analysis_timestamp')}")
            
            # 2. NASA POWER Climate Response
            clim = data.get("climate_summary", {})
            print("\n2. NASA POWER CLIMATE OBSERVATIONS:")
            print(f"   Total Precipitation: {clim.get('total_precip_in')} inches ({clim.get('total_precip_mm')} mm)")
            print(f"   Total Reference ET0: {clim.get('total_et0_in')} inches ({clim.get('total_et0_mm')} mm)")
            print(f"   Water Balance: {clim.get('water_balance_in')} inches ({clim.get('water_balance_status')})")
            print(f"   Growing Degree Days (GDD 50F): {clim.get('total_gdd_f')}")
            print(f"   Max / Min Temperature: {clim.get('max_temperature_c')} C / {clim.get('min_temperature_c')} C")
            print(f"   Extreme Heat Stress Days (>=35C): {clim.get('heat_stress_days_35c')}")
            print(f"   Max Consecutive Dry Days: {clim.get('max_consecutive_dry_days')}")
            
            # 3. USDA SSURGO Soil Profile
            soil = data.get("soil_profile", {})
            print("\n3. USDA SSURGO SOIL PROFILE:")
            print(f"   Map Unit Name: {soil.get('mapunit_name')}")
            print(f"   Dominant Series: {soil.get('dominant_series')}")
            print(f"   Texture Class: {soil.get('texture')}")
            print(f"   Composite Soil Health Score: {soil.get('composite_soil_health_score')} ({soil.get('soil_health_tier')})")
            for ind in soil.get("indicators", []):
                print(f"     - {ind.get('name')}: {ind.get('value')} {ind.get('units')} ({ind.get('rating')})")
            
            # 4. ECMWF ERA5 Reanalysis & Provenance
            era5 = data.get("era5_reanalysis", {})
            print("\n4. ECMWF ERA5 REANALYSIS & PROVENANCE:")
            print(f"   Source: {era5.get('source')} ({era5.get('model_resolution')})")
            print(f"   Observation Date: {era5.get('observation_date')}")
            print(f"   Soil Moisture 0-7cm: {era5.get('soil_moisture_0_to_7cm_m3m3')} m3/m3")
            print(f"   Soil Moisture 7-28cm: {era5.get('soil_moisture_7_to_28cm_m3m3')} m3/m3")
            print(f"   Soil Moisture 28-100cm: {era5.get('soil_moisture_28_to_100cm_m3m3')} m3/m3")
            print(f"   Soil Temperature 0-7cm: {era5.get('soil_temperature_0_to_7cm_c')} C")
            
            # 5. Landsat Raster Observation
            landsat = data.get("landsat_raster_observation", {})
            print("\n5. USGS LANDSAT COLLECTION 2 LEVEL-2 RASTER OBSERVATION:")
            print(f"   Raster Retrieved: {landsat.get('success')}")
            print(f"   Scene ID: {landsat.get('scene_id')}")
            print(f"   Platform: {landsat.get('platform')}")
            print(f"   Acquisition Date: {landsat.get('acquisition_date')}")
            print(f"   Scene Cloud Cover: {landsat.get('scene_cloud_cover_pct')}%")
            metrics = landsat.get("ndvi_metrics", {})
            print(f"   Valid Clear-Sky Pixels: {metrics.get('valid_pixel_count')} / {metrics.get('total_window_pixels')} ({metrics.get('valid_coverage_pct')}%)")
            print(f"   Mean NDVI: {metrics.get('mean_ndvi')}")
            print(f"   Median NDVI: {metrics.get('median_ndvi')}")
            print(f"   Min / Max NDVI: {metrics.get('min_ndvi')} / {metrics.get('max_ndvi')}")
            print(f"   Canopy Vigor Class: {metrics.get('canopy_vigor_classification')}")
            print(f"   Center 3x3 Matrix Sample: {landsat.get('sample_matrix_3x3')}")
            
            # 6. ML Model Dispatch & Suitability Output
            ml = data.get("ml_inferences", {})
            print("\n6. MACHINE LEARNING INFERENCES & DISPATCH:")
            print(f"   Model Version Dispatched: {ml.get('model_version')}")
            print(f"   Satellite Feature Active: {ml.get('satellite_feature_active')}")
            print(f"   NDVI Input Value: {ml.get('landsat_ndvi')}")
            suitabilities = ml.get("crop_suitability", {})
            top_crops = sorted(suitabilities.items(), key=lambda x: x[1].get("suitability_score", 0), reverse=True)[:3]
            bottom_crops = sorted(suitabilities.items(), key=lambda x: x[1].get("suitability_score", 0))[:2]
            print("   Top Recommended Crops:")
            for c, s in top_crops:
                print(f"     - {c.upper()}: {s.get('suitability_score')} ({s.get('status')})")
            print("   Lowest Suitability Crops:")
            for c, s in bottom_crops:
                print(f"     - {c.upper()}: {s.get('suitability_score')} ({s.get('status')})")
                
            # 7. Rotation Recommendations
            engine = data.get("rotation_decision_engine", {})
            print("\n7. ROTATION DECISION ENGINE:")
            print(f"   Primary Recommendation: {engine.get('primary_recommendation')}")
            print(f"   Recommendation Rationale: {engine.get('recommendation_rationale')}")
            strat_b = engine.get("strategies", {}).get("STRATEGY_B", {})
            print(f"   Strategy B Name: {strat_b.get('name')}")
            print(f"   Crop Sequence: {' -> '.join(strat_b.get('crop_sequence', []))}")
            
            # 8. SQLite Persistence Verification
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT id, field_name, latitude, longitude, created_at FROM field_analyses ORDER BY id DESC LIMIT 1;")
            db_fa = cur.fetchone()
            cur.execute("SELECT id, field_id, scene_id, acquisition_date, calculated_indicators, retrieval_timestamp FROM satellite_observations ORDER BY id DESC LIMIT 1;")
            db_sat = cur.fetchone()
            conn.close()
            
            print("\n8. DATABASE PERSISTENCE VERIFICATION:")
            print(f"   Field Analysis Row ID {db_fa[0]}: Name='{db_fa[1]}', Lat={db_fa[2]}, Lon={db_fa[3]}, StoredAt={db_fa[4]}")
            if db_sat:
                sat_ind = json.loads(db_sat[4])
                print(f"   Satellite Row ID {db_sat[0]}: Field='{db_sat[1]}', Scene='{db_sat[2]}', MeanNDVI={sat_ind.get('mean_ndvi')}, StoredAt={db_sat[5]}")
            
            audit_results[loc["id"]] = {
                "status": "SUCCESS",
                "scene_id": landsat.get("scene_id"),
                "mean_ndvi": metrics.get("mean_ndvi"),
                "model_version": ml.get("model_version"),
                "top_crop": top_crops[0][0] if top_crops else None,
                "top_score": top_crops[0][1].get("suitability_score") if top_crops else None
            }
            
        except Exception as e:
            print(f"ERROR FOR {loc['name']}: {e}")
            audit_results[loc["id"]] = {"status": "FAILED", "error": str(e)}
            
    print("\n==================================================")
    print("ALL 3 LOCATIONS COMPLETED")
    print(json.dumps(audit_results, indent=2))
    print("==================================================")

if __name__ == "__main__":
    verify_live_api_3_locations()
