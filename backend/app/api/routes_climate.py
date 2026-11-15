"""
FARMINTEL AI - Climate API Routes
"""

from fastapi import APIRouter, Query, HTTPException
from ..connectors.nasa_power import NasaPowerConnector
from ..engine.processing import DataProcessingEngine
from ..engine.climate_intel import ClimateIntelligenceEngine
from ..models.schemas import ClimateFetchRequest

router = APIRouter(prefix="/api/climate", tags=["Climate Intelligence"])
power_connector = NasaPowerConnector()

@router.post("/fetch")
def fetch_climate_data(payload: ClimateFetchRequest):
    """Fetches real historical NASA POWER daily agroclimatology observations."""
    DataProcessingEngine.validate_coordinates(payload.latitude, payload.longitude)
    res = power_connector.fetch_daily_agroclimatology(
        latitude=payload.latitude,
        longitude=payload.longitude,
        start_date=payload.start_date,
        end_date=payload.end_date,
        use_cache=payload.use_cache
    )
    if not res.get("success"):
        raise HTTPException(status_code=502, detail=res.get("error", "NASA POWER request failed"))
    return res

@router.get("/analyze")
def analyze_climate(
    latitude: float = Query(42.0308, ge=-90.0, le=90.0),
    longitude: float = Query(-93.6319, ge=-180.0, le=180.0),
    start_date: str = Query("20240401"),
    end_date: str = Query("20240930")
):
    """Processes NASA POWER data into GDD, heat stress, ET0, and water balance indicators."""
    raw_res = power_connector.fetch_daily_agroclimatology(latitude, longitude, start_date, end_date)
    if not raw_res.get("success"):
        raise HTTPException(status_code=502, detail=raw_res.get("error", "NASA POWER query failed"))

    df = DataProcessingEngine.process_climate_records(raw_res.get("daily_records", []))
    qc = DataProcessingEngine.assess_data_quality(df)
    indicators = ClimateIntelligenceEngine.calculate_indicators(df)

    return {
        "success": True,
        "cached": raw_res.get("cached", False),
        "location": raw_res.get("location"),
        "date_range": raw_res.get("date_range"),
        "quality_assessment": qc,
        "climate_intelligence": indicators,
        "provenance": raw_res.get("provenance")
    }
