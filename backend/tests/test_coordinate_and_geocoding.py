"""
FARMINTEL AI — Automated Coordinate Integrity, Geocoding & Availability Test Suite
NASA Space Apps Challenge 2026: Field Shift — Adapting Farms with NASA Data

Verifies:
1. Rejection of invalid coordinates (e.g. lon 975.04789, lat 195.0) with HTTP 400 and clear error detail.
2. Multi-tier Reverse Geocoding accuracy across 3 distinct US agricultural regions:
   - Ames, IA (Story County)
   - Fresno, CA (Fresno County)
   - Finney County, KS (Finney County)
3. Dynamic Data Availability Service across 28 official challenge datasets:
   - CONUS vs International coverage gating
   - Verification of AVAILABLE, METADATA_ONLY, and NO_COVERAGE states
4. Dynamic Rotation Optimizer multi-objective objective switching (Profit vs Soil Health vs Resilience).
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.geocoding_service import GeocodingService
from backend.app.services.data_availability_service import DataAvailabilityService
from backend.app.models.schemas import FieldAnalysisRequest

client = TestClient(app)

# =========================================================================
# TEST SUITE 1: STRICT COORDINATE BOUNDS VALIDATION & ERROR FORMATTING
# =========================================================================

def test_rejects_out_of_bounds_longitude():
    """Verify that invalid longitude (such as 975.04789) is strictly rejected with HTTP 400."""
    payload = {
        "latitude": 38.35454,
        "longitude": 975.04789,
        "farmer_priority": "soil_health"
    }
    response = client.post("/api/field/analyze", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    # Ensure error is a readable formatted string and NOT [object Object]
    assert isinstance(data["detail"], str)
    assert "Longitude must be between -180" in data["detail"]
    assert "975.04789" in data["detail"]


def test_rejects_out_of_bounds_latitude():
    """Verify that latitude > 90 is rejected with HTTP 400."""
    payload = {
        "latitude": 195.45,
        "longitude": -93.63,
        "farmer_priority": "soil_health"
    }
    response = client.post("/api/field/analyze", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert isinstance(data["detail"], str)
    assert "Latitude must be between -90" in data["detail"]


def test_reverse_geocode_endpoint_rejects_invalid_coords():
    """GET /api/field/reverse-geocode must reject out-of-bounds coordinates with HTTP 400."""
    response = client.get("/api/field/reverse-geocode?latitude=42.0&longitude=250.0")
    assert response.status_code == 400
    data = response.json()
    assert "Longitude must be between -180 and 180" in data["detail"]


# =========================================================================
# TEST SUITE 2: REVERSE GEOCODING RESOLUTION ACROSS 3 AG REGIONS
# =========================================================================

def test_reverse_geocode_ames_iowa():
    """Ames, IA (42.0308, -93.6319) must resolve to Story County, Iowa."""
    result = GeocodingService.reverse_geocode(42.0308, -93.6319)
    assert result["success"] is True
    assert "Story" in result["county"]
    assert result["state"] == "Iowa"
    assert result["state_code"] == "IA"
    assert result["country"] == "United States"


def test_reverse_geocode_fresno_california():
    """Fresno, CA (36.7468, -119.7726) must resolve to Fresno County, California."""
    result = GeocodingService.reverse_geocode(36.7468, -119.7726)
    assert result["success"] is True
    assert "Fresno" in result["county"]
    assert result["state"] == "California"
    assert result["state_code"] == "CA"


def test_reverse_geocode_finney_kansas():
    """Finney County, KS (37.9717, -100.8654) must resolve to Finney County, Kansas."""
    result = GeocodingService.reverse_geocode(37.9717, -100.8654)
    assert result["success"] is True
    assert "Finney" in result["county"]
    assert result["state"] == "Kansas"
    assert result["state_code"] == "KS"


# =========================================================================
# TEST SUITE 3: DYNAMIC 28-DATASET AVAILABILITY SERVICE
# =========================================================================

def test_data_availability_conus():
    """For Ames, IA, dynamic availability must return all 28 datasets with expected availability."""
    avail = DataAvailabilityService.check_availability(42.0308, -93.6319)
    assert avail["success"] is True
    assert avail["total_datasets"] == 28
    
    counts = avail["summary_counts"]
    assert counts["AVAILABLE"] >= 4  # NASA POWER, SSURGO, ERA5, Landsat
    assert counts["NO_COVERAGE"] == 0  # Ames is inside CONUS

    # Check key individual datasets
    ds_map = {d["dataset_id"]: d for d in avail["datasets"]}
    assert ds_map["DS_NASA_POWER"]["status"] == "AVAILABLE"
    assert ds_map["DS_USDA_SSURGO"]["status"] == "AVAILABLE"
    assert ds_map["DS_ECMWF_ERA5"]["status"] == "AVAILABLE"
    assert ds_map["DS_USGS_LANDSAT"]["status"] == "AVAILABLE"
    assert ds_map["DS_NASA_SMAP"]["status"] == "METADATA_ONLY"


def test_data_availability_outside_conus():
    """For an international location (e.g. Europe), SSURGO and NWIS must report NO_COVERAGE."""
    avail = DataAvailabilityService.check_availability(48.8566, 2.3522)
    assert avail["success"] is True
    assert avail["total_datasets"] == 28
    
    counts = avail["summary_counts"]
    assert counts["NO_COVERAGE"] >= 2  # SSURGO and NWIS have no coverage outside US
    
    ds_map = {d["dataset_id"]: d for d in avail["datasets"]}
    assert ds_map["DS_USDA_SSURGO"]["status"] == "NO_COVERAGE"
    assert ds_map["DS_USGS_NWIS"]["status"] == "NO_COVERAGE"
    assert ds_map["DS_NASA_POWER"]["status"] == "AVAILABLE"  # NASA POWER is global


# =========================================================================
# TEST SUITE 4: DYNAMIC MULTI-OBJECTIVE ROTATION OPTIMIZER
# =========================================================================

def test_dynamic_rotation_objective_switching():
    """
    Evaluates that switching strategic priority (Profit vs Soil Health vs Resilience)
    dynamically activates distinct winning strategies and Pareto metrics.
    """
    # 1. Economic Profit evaluation
    resp_profit = client.post("/api/field/analyze", json={
        "latitude": 42.0308,
        "longitude": -93.6319,
        "farmer_priority": "economic_profit",
        "previous_crop": "soybeans"
    })
    assert resp_profit.status_code == 200
    engine_profit = resp_profit.json()["rotation_decision_engine"]
    assert engine_profit["primary_recommendation"] == "STRATEGY_A"

    # 2. Soil Health evaluation
    resp_soil = client.post("/api/field/analyze", json={
        "latitude": 42.0308,
        "longitude": -93.6319,
        "farmer_priority": "soil_health",
        "previous_crop": "corn"
    })
    assert resp_soil.status_code == 200
    engine_soil = resp_soil.json()["rotation_decision_engine"]
    assert engine_soil["primary_recommendation"] == "STRATEGY_B"

    # 3. Climate Resilience evaluation
    resp_resil = client.post("/api/field/analyze", json={
        "latitude": 42.0308,
        "longitude": -93.6319,
        "farmer_priority": "climate_resilience",
        "previous_crop": "soybeans"
    })
    assert resp_resil.status_code == 200
    engine_resil = resp_resil.json()["rotation_decision_engine"]
    assert engine_resil["primary_recommendation"] == "STRATEGY_C"


# =========================================================================
# TEST SUITE 5: INTERNATIONAL AGRICULTURAL ANALYSIS FOR OTHER COUNTRIES
# =========================================================================

def test_international_field_analysis_india():
    """Verify end-to-end analysis for Punjab, India using global NASA & ERA5 observations."""
    payload = {
        "field_name": "Punjab Wheat-Rice Field",
        "latitude": 30.9010,
        "longitude": 75.8573,
        "farmer_priority": "soil_health",
        "previous_crop": "winter_wheat",
        "analysis_year": 2024
    }
    resp = client.post("/api/field/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["geospatial_context"]["is_conus_covered"] is False
    assert data["field_profile"]["country"] == "India"
    assert data["climate_summary"]["total_gdd_f"] > 4000
    assert data["rotation_decision_engine"]["primary_recommendation"] in ["STRATEGY_A", "STRATEGY_B", "STRATEGY_C"]


def test_international_field_analysis_france():
    """Verify end-to-end analysis for Beauce, France using global NASA & ERA5 observations."""
    payload = {
        "field_name": "Beauce Wheat Plain",
        "latitude": 48.4439,
        "longitude": 1.4890,
        "farmer_priority": "economic_profit",
        "previous_crop": "winter_wheat",
        "analysis_year": 2024
    }
    resp = client.post("/api/field/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["geospatial_context"]["is_conus_covered"] is False
    assert data["field_profile"]["country"] == "France"
    assert data["climate_summary"]["total_gdd_f"] > 1000
