"""
FARMINTEL AI - Automated Verification & Test Suite
Covers:
1. Coordinate & parameter validation
2. Live NASA POWER API connection & response parsing
3. Missing observation handling
4. Climate indicator calculations (GDD, Heat Stress, ET0, Water Balance)
5. USDA SSURGO Soil Data Access live spatial query
6. Crop catalog integrity & suitability filtering
7. 3-Strategy Crop Rotation Decision Engine
8. FastAPI endpoints validation
"""

import pytest
import sys
import os
import pandas as pd
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.engine.processing import DataProcessingEngine
from backend.app.connectors.nasa_power import NasaPowerConnector
from backend.app.connectors.usda_ssurgo import UsdaSsurgoConnector
from backend.app.connectors.registry import DataSourceRegistry
from backend.app.engine.climate_intel import ClimateIntelligenceEngine
from backend.app.engine.soil_intel import SoilIntelligenceEngine
from backend.app.engine.crop_knowledge import CropKnowledgeEngine
from backend.app.engine.rotation_decision import RotationDecisionEngine
from backend.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# --- 1. Coordinate & Validation Tests ---
def test_coordinate_validation():
    assert DataProcessingEngine.validate_coordinates(42.0308, -93.6319) is True
    assert DataProcessingEngine.is_within_usa(42.0308, -93.6319) is True
    assert DataProcessingEngine.is_within_usa(64.2008, -149.4937) is True # Alaska
    assert DataProcessingEngine.is_within_usa(0.0, 0.0) is False

    with pytest.raises(ValueError):
        DataProcessingEngine.validate_coordinates(95.0, -93.6319)

# --- 2. Live NASA POWER Connection Test ---
def test_live_nasa_power_connection():
    connector = NasaPowerConnector()
    res = connector.fetch_daily_agroclimatology(42.0308, -93.6319, "20240601", "20240607", use_cache=True)
    assert res.get("success") is True or "daily_records" in res
    if res.get("success"):
        assert "T2M" in res["summary_statistics"]
        assert len(res["daily_records"]) >= 5

# --- 3. Missing Observation & Processing Test ---
def test_missing_observation_handling():
    synthetic_records = [
        {"date": "2024-05-01", "T2M": 15.0, "T2M_MAX": 22.0, "T2M_MIN": 8.0, "PRECTOTCORR": 0.0, "ALLSKY_SFC_SW_DWN": 16.0},
        {"date": "2024-05-02", "T2M": None, "T2M_MAX": None, "T2M_MIN": None, "PRECTOTCORR": 2.5, "ALLSKY_SFC_SW_DWN": 14.0},
        {"date": "2024-05-03", "T2M": 17.0, "T2M_MAX": 24.0, "T2M_MIN": 10.0, "PRECTOTCORR": 0.0, "ALLSKY_SFC_SW_DWN": 18.0}
    ]
    df = DataProcessingEngine.process_climate_records(synthetic_records)
    assert df["T2M"].isna().sum() == 0
    assert df.loc[1, "T2M"] == 15.0

# --- 4. Climate Indicator Calculations Test ---
def test_climate_indicators():
    records = [
        {"date": f"2024-06-{i:02d}", "T2M": 22.0, "T2M_MAX": 36.0, "T2M_MIN": 14.0, "PRECTOTCORR": 0.0 if i < 5 else 12.0, "ALLSKY_SFC_SW_DWN": 20.0}
        for i in range(1, 11)
    ]
    df = DataProcessingEngine.process_climate_records(records)
    indicators = ClimateIntelligenceEngine.calculate_indicators(df)
    summary = indicators["summary"]
    assert summary["total_gdd_f"] > 0
    assert summary["heat_stress_days_35c"] == 10
    assert summary["total_precip_mm"] == 12.0 * 6
    assert summary["total_et0_mm"] > 0

# --- 5. USDA SSURGO Soil Data Access Test ---
def test_usda_ssurgo_live_query():
    ssurgo = UsdaSsurgoConnector()
    res = ssurgo.fetch_soil_profile(42.0308, -93.6319, use_cache=True)
    assert res["success"] is True
    assert "mapunit" in res
    assert "topsoil_properties" in res
    topsoil = res["topsoil_properties"]
    assert 4.0 <= topsoil["ph_water"] <= 9.0
    assert topsoil["organic_matter_pct"] > 0
    assert "texture_class" in topsoil

# --- 6. Crop Knowledge Catalog Test ---
def test_crop_knowledge_catalog():
    crops = CropKnowledgeEngine.get_all_crops()
    assert len(crops) >= 8
    corn = CropKnowledgeEngine.get_crop_by_id("corn")
    assert corn is not None
    assert corn["nitrogen_fixing"] is False
    assert corn["gdd_requirement_f"] >= 2000

    soy = CropKnowledgeEngine.get_crop_by_id("soybeans")
    assert soy["nitrogen_fixing"] is True
    assert soy["nitrogen_credit_lb_ac"] > 0

# --- 7. Crop Rotation Decision Engine Test ---
def test_rotation_decision_engine():
    mock_climate = {
        "summary": {
            "total_gdd_f": 2600,
            "total_precip_in": 24.0,
            "total_et0_in": 21.0,
            "water_balance_mm": 76.0,
            "heat_stress_days_35c": 3,
            "max_consecutive_dry_days": 10
        }
    }
    mock_soil = {
        "success": True,
        "mapunit": {"name": "Clarion loam, 2 to 5 percent slopes"},
        "dominant_component": {"name": "Clarion", "drainage_class": "Well drained", "hydrologic_group": "B"},
        "topsoil_properties": {"ph_water": 6.8, "organic_matter_pct": 3.8, "texture_class": "Loam"},
        "profile_metrics": {"total_available_water_capacity_100cm_cm": 20.5},
        "agronomic_limitations": []
    }
    res = RotationDecisionEngine.generate_recommendations(mock_climate, mock_soil, "Test Field", "Iowa")
    assert "strategies" in res
    strategies = res["strategies"]
    assert "strategy_a" in strategies
    assert "strategy_b" in strategies
    assert "strategy_c" in strategies
    assert len(res["comparison_matrix"]) >= 5
    exp_b = strategies["strategy_b"]["explainability"]
    assert "why_suggested" in exp_b
    assert "supporting_observations" in exp_b
    assert "expected_benefits" in exp_b
    assert "inherent_risks" in exp_b
    assert exp_b["confidence_score"] >= 80

# --- 8. FastAPI Endpoints Test ---
def test_fastapi_endpoints():
    h_resp = client.get("/api/health")
    assert h_resp.status_code == 200
    assert h_resp.json()["status"] == "HEALTHY"

    d_resp = client.get("/api/datasets")
    assert d_resp.status_code == 200
    assert len(d_resp.json()["datasets"]) >= 5

    c_resp = client.get("/api/crops")
    assert c_resp.status_code == 200
    assert c_resp.json()["count"] >= 8

    s_resp = client.get("/api/soil/analyze?latitude=42.0308&longitude=-93.6319")
    assert s_resp.status_code == 200
    assert s_resp.json()["success"] is True

    e_resp = client.get("/api/rotation/explanation?strategy_id=STRATEGY_B&latitude=42.0308&longitude=-93.6319")
    assert e_resp.status_code == 200
    assert e_resp.json()["strategy_id"] == "STRATEGY_B"

# --- 9. Official 28-Source Registry Test ---
def test_official_registry_completeness():
    import os
    import json
    import pandas as pd

    reg_resp = client.get("/api/datasets/registry")
    assert reg_resp.status_code == 200
    reg_json = reg_resp.json()
    assert reg_json["success"] is True
    assert reg_json["count"] == 28
    assert len(reg_json["datasets"]) == 28

    # Verify JSON and CSV file persistence
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    json_path = os.path.join(base_dir, "backend", "data", "official_data_sources_registry.json")
    csv_path = os.path.join(base_dir, "backend", "data", "official_data_sources_registry.csv")

    assert os.path.exists(json_path), f"Missing registry JSON at {json_path}"
    assert os.path.exists(csv_path), f"Missing registry CSV at {csv_path}"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 28

    df = pd.read_csv(csv_path)
    assert len(df) == 28
    assert "DS_NASA_POWER" in df["dataset_id"].values
    assert "DS_USDA_SSURGO" in df["dataset_id"].values
    assert "DS_ESA_SENTINEL2" in df["dataset_id"].values

