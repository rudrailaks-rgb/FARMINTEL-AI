"""
FARMINTEL AI - Machine Learning Models & Inference API Routes
NASA Space Apps Challenge 2026: Field Shift — Adapting Farms with NASA Data
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ..ml.model_registry import AgriculturalMLRegistry, CANDIDATE_CROPS
from ..engine.crop_knowledge import CropKnowledgeEngine

router = APIRouter(prefix="/api/ml", tags=["Machine Learning Intelligence"])
registry = AgriculturalMLRegistry()

class CustomFeaturePredictionRequest(BaseModel):
    gdd_base50_f: float = Field(2600.0, ge=500.0, le=6000.0)
    mean_temp_c: float = Field(18.5, ge=0.0, le=45.0)
    heat_stress_days_35c: float = Field(2.0, ge=0.0, le=60.0)
    total_precip_in: float = Field(22.0, ge=1.0, le=100.0)
    et0_in: float = Field(20.0, ge=1.0, le=60.0)
    water_balance_in: float = Field(2.0, ge=-50.0, le=50.0)
    max_dry_spell_days: float = Field(12.0, ge=0.0, le=90.0)
    topsoil_sand_pct: float = Field(35.0, ge=0.0, le=100.0)
    topsoil_silt_pct: float = Field(40.0, ge=0.0, le=100.0)
    topsoil_clay_pct: float = Field(25.0, ge=0.0, le=100.0)
    topsoil_ph: float = Field(6.5, ge=3.5, le=10.0)
    topsoil_om_pct: float = Field(3.2, ge=0.1, le=15.0)
    profile_awc_cm: float = Field(18.5, ge=1.0, le=50.0)
    drainage_class_num: float = Field(3.0, ge=1.0, le=4.0)
    hydrologic_group_num: float = Field(2.0, ge=1.0, le=4.0)
    landsat_ndvi: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Optional USGS Landsat 8-9 Surface Reflectance NDVI (triggers v2.1 model)")

@router.get("/models")
def get_ml_models_metadata():
    """
    Returns full evaluation metrics, cross-validation scores, R^2, accuracy,
    confusion matrices, and feature importances for all trained models,
    including the versioned v2.1 Satellite-Enhanced Landsat NDVI benchmark.
    """
    metadata = registry.get_models_metadata()
    return {
        "success": True,
        "pipeline_version": "2.1.0-SATELLITE-ENHANCED",
        "dataset_summary": {
            "total_records": 2550,
            "agricultural_production_zones": 17,
            "temporal_range": "2018-2024",
            "features_count": 16,
            "target_crops_count": 10,
            "satellite_sensor": "USGS / NASA Landsat 8-9 Collection 2 Level-2 Surface Reflectance (SR_B4 & SR_B5)"
        },
        "models": metadata.get("models", {}),
        "satellite_benchmark": metadata.get("models", {}).get("satellite_benchmark")
    }

@router.post("/predict")
def predict_custom_features(payload: CustomFeaturePredictionRequest):
    """
    Executes real-time inference using the trained multi-model ensemble on custom
    agroclimatic and edaphic features. If landsat_ndvi is provided, automatically uses v2.1.
    """
    try:
        # Create mock climate and soil dictionaries that map to the feature vector
        climate_summary = {
            "total_gdd_f": payload.gdd_base50_f,
            "mean_temperature_c": payload.mean_temp_c,
            "heat_stress_days_35c": payload.heat_stress_days_35c,
            "total_precip_in": payload.total_precip_in,
            "total_et0_in": payload.et0_in,
            "water_balance_in": payload.water_balance_in,
            "max_consecutive_dry_days": payload.max_dry_spell_days
        }
        soil_profile = {
            "topsoil_properties": {
                "sand_pct": payload.topsoil_sand_pct,
                "silt_pct": payload.topsoil_silt_pct,
                "clay_pct": payload.topsoil_clay_pct,
                "ph_water": payload.topsoil_ph,
                "organic_matter_pct": payload.topsoil_om_pct
            },
            "profile_metrics": {
                "total_available_water_capacity_100cm_cm": payload.profile_awc_cm
            },
            "dominant_component": {
                "drainage_class": "well drained" if payload.drainage_class_num >= 3 else "somewhat poorly drained",
                "hydrologic_group": ["a", "b", "c", "d"][min(int(payload.hydrologic_group_num) - 1, 3)]
            }
        }
        predictions = registry.predict_all(climate_summary, soil_profile, landsat_ndvi=payload.landsat_ndvi)
        return {
            "success": True,
            "predictions": predictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML Inference error: {str(e)}")

@router.get("/crops")
def get_candidate_crops_catalog():
    """
    Returns agronomic parameters for all 10 candidate rotation crops,
    including botanical family, water requirements, rooting depth,
    GDD requirements, and biological nitrogen fixation.
    """
    crops_catalog = []
    for crop in CANDIDATE_CROPS:
        data = CropKnowledgeEngine.get_crop_by_id(crop) or {}
        crops_catalog.append({
            "crop_id": crop,
            "common_name": data.get("common_name", crop.title()),
            "scientific_name": data.get("name", "N/A"),
            "category": data.get("category", "Field Crop"),
            "lifecycle": data.get("lifecycle", "Annual"),
            "water_requirement_in": data.get("water_requirement_in", 20.0),
            "gdd_requirement_f": data.get("gdd_requirement_f", 2200),
            "nitrogen_credit_lb_ac": data.get("nitrogen_credit_lb_ac", 0),
            "drought_tolerance": data.get("drought_tolerance", "Moderate"),
            "rotation_benefits": data.get("rotation_benefits", "Crop diversity")
        })

    return {
        "success": True,
        "count": len(crops_catalog),
        "crops": crops_catalog
    }
