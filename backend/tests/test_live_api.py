"""
FARMINTEL AI - End-to-End API Integration Test
Tests /api/field/analyze, /api/rotation/compare, /api/ml/models across multiple regions.
"""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"

def test_ml_models():
    res = client.get("/api/ml/models")
    assert res.status_code == 200
    data = res.json()
    assert "crop_suitability" in data["models"]
    assert "climate_risk" in data["models"]
    assert "yield_performance" in data["models"]

def test_iowa_field_analyze():
    payload = {
        "latitude": 42.0308,
        "longitude": -93.6319,
        "field_name": "Ames Research Field",
        "previous_crop": "corn",
        "farmer_priority": "soil_health",
        "analysis_year": 2024
    }
    res = client.post("/api/field/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "field_id" in data["geospatial_context"]
    assert data["geospatial_context"]["is_conus_covered"] is True

    # Check rotation engine has 3 strategies
    strategies = data["rotation_decision_engine"]["strategies"]
    assert "strategy_a" in strategies
    assert "strategy_b" in strategies
    assert "strategy_c" in strategies

    for s_key, s_data in strategies.items():
        assert len(s_data["rotation_sequence"]) >= 3
        # Check confidence is in [0, 100]
        conf = s_data["explainability"]["confidence_score"]
        assert 0 <= conf <= 100

    # Check ML inferences are populated
    assert "crop_suitability" in data["ml_inferences"]
    assert len(data["ml_inferences"]["crop_suitability"]) == 10

def test_california_field_analyze():
    payload = {
        "latitude": 36.7468,
        "longitude": -119.7726,
        "field_name": "Fresno Central Valley Field",
        "previous_crop": "alfalfa",
        "farmer_priority": "climate_resilience",
        "analysis_year": 2024
    }
    res = client.post("/api/field/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    strategies = data["rotation_decision_engine"]["strategies"]
    # Check that strategies are generated dynamically
    strat_c = strategies["strategy_c"]
    assert len(strat_c["rotation_sequence"]) >= 3

def test_alberta_fallback_analyze():
    # Outside CONUS - test SSURGO benchmark fallback
    payload = {
        "latitude": 58.30949,
        "longitude": -116.82103,
        "field_name": "High Level Alberta",
        "previous_crop": "barley",
        "farmer_priority": "balanced",
        "analysis_year": 2024
    }
    res = client.post("/api/field/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["geospatial_context"]["is_conus_covered"] is False

if __name__ == "__main__":
    print("Running integration tests...")
    test_health()
    print("Health passed.")
    test_ml_models()
    print("ML models passed.")
    test_iowa_field_analyze()
    print("Iowa field analysis passed.")
    test_california_field_analyze()
    print("California field analysis passed.")
    test_alberta_fallback_analyze()
    print("Alberta fallback analysis passed.")
    print("ALL API INTEGRATION TESTS PASSED SUCCESSFULLY!")
