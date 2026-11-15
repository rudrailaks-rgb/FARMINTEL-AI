"""
FARMINTEL AI - Crop Rotation Decision Engine API Routes
Multi-Objective Constrained Sequence Optimization and Granular Evidence Tracing
"""

from fastapi import APIRouter, Query, HTTPException
from ..connectors.nasa_power import NasaPowerConnector
from ..connectors.usda_ssurgo import UsdaSsurgoConnector
from ..engine.processing import DataProcessingEngine
from ..engine.climate_intel import ClimateIntelligenceEngine
from ..engine.rotation_optimizer import RotationOptimizer
from ..models.field_state import FieldState
from ..models.schemas import RotationCompareRequest

router = APIRouter(prefix="/api/rotation", tags=["Crop Rotation Decision Engine"])
power_connector = NasaPowerConnector()
ssurgo_connector = UsdaSsurgoConnector()
optimizer = RotationOptimizer()

@router.post("/compare")
def compare_rotation_strategies(payload: RotationCompareRequest):
    """
    Evaluates Strategy A (Baseline Economic), Strategy B (Soil Improvement), and Strategy C (Climate-Resilient).
    Uses the constrained multi-objective sequence optimizer and scikit-learn ML suitability ensemble.
    Returns comparative scoring, water demand, N credit, and risk trade-offs.
    """
    field_state = FieldState.create(
        latitude=payload.latitude,
        longitude=payload.longitude,
        field_name=payload.field_name,
        analysis_year=payload.analysis_year or 2024,
        previous_crop=payload.previous_crop or "corn",
        farmer_priority=payload.farmer_priority or "balanced"
    )

    year = field_state.analysis_year
    start_date = f"{year}0401"
    end_date = f"{year}0930"

    climate_res = power_connector.fetch_daily_agroclimatology(
        field_state.latitude, field_state.longitude, start_date, end_date, use_cache=True
    )
    df_climate = DataProcessingEngine.process_climate_records(climate_res.get("daily_records", []))
    climate_intel = ClimateIntelligenceEngine.calculate_indicators(df_climate)

    soil_res = ssurgo_connector.fetch_soil_profile(field_state.latitude, field_state.longitude, use_cache=True)
    if not soil_res.get("success"):
        soil_res = ssurgo_connector.get_fallback_profile(field_state.latitude, field_state.longitude)

    recommendations = optimizer.optimize(
        climate_summary=climate_intel.get("summary", {}),
        soil_profile=soil_res,
        previous_crop=field_state.previous_crop,
        farmer_priority=field_state.farmer_priority,
        field_name=field_state.field_name,
        latitude=field_state.latitude,
        longitude=field_state.longitude,
        analysis_year=year
    )

    return {
        "success": True,
        "field_id": field_state.field_id,
        "geospatial_hash": field_state.geospatial_hash,
        "recommendations": recommendations
    }

@router.get("/explanation")
def get_strategy_explanation(
    strategy_id: str = Query("STRATEGY_B", description="STRATEGY_A, STRATEGY_B, or STRATEGY_C"),
    latitude: float = Query(42.0308),
    longitude: float = Query(-93.6319)
):
    """
    Returns granular, scientifically defensible evidence tracing, observations,
    expected benefits, risks, confidence score, and farmer validation checklist.
    """
    field_state = FieldState.create(latitude=latitude, longitude=longitude)
    climate_res = power_connector.fetch_daily_agroclimatology(
        field_state.latitude, field_state.longitude, "20240401", "20240930", use_cache=True
    )
    df_climate = DataProcessingEngine.process_climate_records(climate_res.get("daily_records", []))
    climate_intel = ClimateIntelligenceEngine.calculate_indicators(df_climate)
    soil_res = ssurgo_connector.fetch_soil_profile(field_state.latitude, field_state.longitude, use_cache=True)
    if not soil_res.get("success"):
        soil_res = ssurgo_connector.get_fallback_profile(field_state.latitude, field_state.longitude)

    recs = optimizer.optimize(
        climate_summary=climate_intel.get("summary", {}),
        soil_profile=soil_res,
        latitude=field_state.latitude,
        longitude=field_state.longitude
    )
    strategies = recs.get("strategies", {})

    target_key = strategy_id.lower()
    if target_key not in strategies:
        raise HTTPException(status_code=404, detail=f"Strategy not found: {strategy_id}. Must be STRATEGY_A, STRATEGY_B, or STRATEGY_C")

    strat = strategies[target_key]
    return {
        "success": True,
        "field_id": field_state.field_id,
        "strategy_id": strat.get("strategy_id"),
        "strategy_name": strat.get("name"),
        "rotation_sequence": strat.get("rotation_sequence"),
        "metrics": strat.get("metrics"),
        "explainability": strat.get("explainability"),
        "environmental_context": recs.get("environmental_context")
    }
