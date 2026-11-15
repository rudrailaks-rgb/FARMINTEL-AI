import sys
import os
import json
import joblib
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.ml.model_registry import AgriculturalMLRegistry, FEATURE_NAMES, CANDIDATE_CROPS

def verify_ml_models():
    print("==================================================")
    print("STEP 2: MACHINE LEARNING MODEL ARCHITECTURE AUDIT")
    print("==================================================")
    
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "data", "models"))
    v20_path = os.path.join(models_dir, "crop_suitability_model.joblib")
    v21_path = os.path.join(models_dir, "crop_suitability_model_v21_satellite.joblib")
    
    print(f"Loading v2.0 baseline model: {v20_path}")
    assert os.path.exists(v20_path), f"Missing v2.0 model at {v20_path}"
    model_v20 = joblib.load(v20_path)
    print(f"  Model Object: {type(model_v20)}")
    print(f"  Estimators Count: {len(model_v20.estimators_)}")
    print(f"  Feature count expected: {model_v20.n_features_in_}")
    print(f"  Base 15 Features: {FEATURE_NAMES}")
    
    print(f"\nLoading v2.1 satellite-enhanced model: {v21_path}")
    assert os.path.exists(v21_path), f"Missing v2.1 model at {v21_path}"
    model_v21 = joblib.load(v21_path)
    print(f"  Model Object: {type(model_v21)}")
    print(f"  Estimators Count: {len(model_v21.estimators_)}")
    print(f"  Feature count expected: {model_v21.n_features_in_}")
    v21_features = FEATURE_NAMES + ["landsat_ndvi"]
    print(f"  Exact feature list (ordered, 16 features):")
    for idx, fname in enumerate(v21_features, 1):
        print(f"    {idx:2d}. {fname}")
        
    print("\nFeature Importances (v2.1):")
    importances = model_v21.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    for rank, idx in enumerate(sorted_idx, 1):
        print(f"    Rank {rank:2d}: {v21_features[idx]:<25} = {importances[idx]*100:6.2f}%")
        
    # Test dynamic dispatch in AgriculturalMLRegistry
    print("\n--------------------------------------------------")
    print("TESTING DYNAMIC DISPATCH & FALLBACK IN REGISTRY")
    print("--------------------------------------------------")
    registry = AgriculturalMLRegistry()
    
    # Climate and soil profiles for testing
    climate_ames = {
        "annual_gdd": 3150.0,
        "mean_temp_c": 10.5,
        "heat_stress_days": 4,
        "annual_rainfall_inches": 34.5,
        "annual_et0_inches": 28.4,
        "max_dry_spell_days": 11
    }
    soil_ames = {
        "sand_pct": 18.0,
        "silt_pct": 58.0,
        "clay_pct": 24.0,
        "ph": 6.8,
        "organic_matter_pct": 4.2,
        "available_water_capacity_profile": 22.0,
        "primary_component": {
            "drainage_class": "well drained",
            "hydrologic_group": "B"
        }
    }
    
    # A) Call with landsat_ndvi = 0.77 (should dispatch v2.1)
    res_v21 = registry.predict_all(climate_ames, soil_ames, landsat_ndvi=0.77)
    print("A) With landsat_ndvi = 0.77 (Ames IA June):")
    print(f"   Model Version Used: {res_v21.get('model_version')}")
    print(f"   Satellite Feature Active: {res_v21.get('satellite_feature_active')}")
    print(f"   Landsat NDVI Passed: {res_v21.get('landsat_ndvi')}")
    print(f"   Features Used Count: {len(res_v21.get('features_used', {}))}")
    print(f"   Corn Score: {res_v21['crop_suitability']['corn']['suitability_score']} ({res_v21['crop_suitability']['corn']['status']})")
    print(f"   Soybean Score: {res_v21['crop_suitability']['soybeans']['suitability_score']} ({res_v21['crop_suitability']['soybeans']['status']})")
    assert res_v21.get("model_version") == "v2.1_satellite_enhanced"
    assert res_v21.get("satellite_feature_active") is True
    
    # B) Call with landsat_ndvi = None (should cleanly fallback to v2.0 baseline)
    res_v20 = registry.predict_all(climate_ames, soil_ames, landsat_ndvi=None)
    print("\nB) With landsat_ndvi = None (Cloud/Missing Satellite Fallback):")
    print(f"   Model Version Used: {res_v20.get('model_version')}")
    print(f"   Satellite Feature Active: {res_v20.get('satellite_feature_active')}")
    print(f"   Landsat NDVI Passed: {res_v20.get('landsat_ndvi')}")
    print(f"   Features Used Count: {len(res_v20.get('features_used', {}))}")
    print(f"   Corn Score: {res_v20['crop_suitability']['corn']['suitability_score']} ({res_v20['crop_suitability']['corn']['status']})")
    print(f"   Soybean Score: {res_v20['crop_suitability']['soybeans']['suitability_score']} ({res_v20['crop_suitability']['soybeans']['status']})")
    assert res_v20.get("model_version") == "v2.0_climate_soil_baseline"
    assert res_v20.get("satellite_feature_active") is False
    
    # Benchmark JSON inspection
    bm_path = os.path.join(models_dir, "satellite_enhanced_model_benchmark.json")
    assert os.path.exists(bm_path)
    with open(bm_path, "r") as f:
        bm = json.load(f)
    print("\n--------------------------------------------------")
    print("INSPECTING GEOGRAPHIC BENCHMARK & DATASET PROVENANCE")
    print("--------------------------------------------------")
    print(f"Model ID: {bm.get('model_id')}")
    print(f"Training Provenance: {bm.get('training_set_provenance')}")
    print(f"Validation Provenance: {bm.get('validation_set_provenance')}")
    print(f"Synthetic Data Warning: {bm.get('synthetic_data_statement')}")
    print(f"Performance Comparison: v2.0 MAE={bm.get('metrics', {}).get('mae_v20_baseline')} vs v2.1 MAE={bm.get('metrics', {}).get('mae_v21_satellite')}")
    print(f"Required Ground Truth for True Validation: {bm.get('required_ground_truth_for_operational_validation')}")
    
    print("\n[STEP 2 VERIFICATION RESULT: SUCCESS]")

if __name__ == "__main__":
    verify_ml_models()
