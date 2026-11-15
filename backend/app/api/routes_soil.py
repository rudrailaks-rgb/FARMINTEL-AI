"""
FARMINTEL AI - Soil API Routes
"""

from fastapi import APIRouter, Query, HTTPException
from ..connectors.usda_ssurgo import UsdaSsurgoConnector
from ..engine.soil_intel import SoilIntelligenceEngine
from ..engine.processing import DataProcessingEngine

router = APIRouter(prefix="/api/soil", tags=["Soil Intelligence"])
ssurgo_connector = UsdaSsurgoConnector()

@router.get("/analyze")
def analyze_soil(
    latitude: float = Query(42.0308, ge=-90.0, le=90.0),
    longitude: float = Query(-93.6319, ge=-180.0, le=180.0)
):
    """Retrieves and evaluates official USDA NRCS SSURGO soil characteristics."""
    DataProcessingEngine.validate_coordinates(latitude, longitude)
    raw_soil = ssurgo_connector.fetch_soil_profile(latitude, longitude)
    if not raw_soil.get("success"):
        raise HTTPException(status_code=404, detail=raw_soil.get("error", "Soil data unavailable"))

    evaluated = SoilIntelligenceEngine.evaluate_soil_health(raw_soil)
    return {
        "success": True,
        "cached": raw_soil.get("cached", False),
        "raw_ssurgo": raw_soil,
        "soil_intelligence": evaluated
    }
