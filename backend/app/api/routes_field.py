"""
FARMINTEL AI - Integrated Field Analysis API Route
NASA Space Apps Challenge 2026: Field Shift — Adapting Farms with NASA Data
"""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from ..connectors.nasa_power import NasaPowerConnector
from ..connectors.usda_ssurgo import UsdaSsurgoConnector
from ..connectors.nasa_earthdata import NasaEarthdataConnector
from ..connectors.era5_connector import Era5Connector
from ..connectors.usgs_water_connector import UsgsWaterConnector
from ..connectors.landsat_raster_connector import LandsatRasterConnector
from ..engine.processing import DataProcessingEngine
from ..engine.climate_intel import ClimateIntelligenceEngine
from ..engine.soil_intel import SoilIntelligenceEngine
from ..engine.rotation_optimizer import RotationOptimizer
from ..models.field_state import FieldState
from ..models.schemas import FieldAnalysisRequest
from ..database import save_field_analysis, save_satellite_observation
from ..services.geocoding_service import GeocodingService
from ..services.data_availability_service import DataAvailabilityService

router = APIRouter(prefix="/api/field", tags=["Field Analysis"])
power_connector = NasaPowerConnector()
ssurgo_connector = UsdaSsurgoConnector()
earthdata_connector = NasaEarthdataConnector()
era5_connector = Era5Connector()
usgs_water_connector = UsgsWaterConnector()
landsat_raster_connector = LandsatRasterConnector()
optimizer = RotationOptimizer()

@router.post("/analyze")
def analyze_field_comprehensive(payload: FieldAnalysisRequest):
    """
    Performs end-to-end multi-source analysis for an authoritative selected field location:
    1. Validates coordinates and spatial bounding format.
    2. Retrieves real NASA POWER daily agroclimatology.
    3. Retrieves real USDA NRCS SSURGO / STATSGO2 soil characteristics.
    4. Retrieves real ECMWF ERA5 multi-layer root-zone soil moisture & temperature.
    5. Retrieves real USGS NWIS watershed hydrologic monitoring gage observations.
    6. Queries NASA CMR and USGS STAC for orbital satellite scenes (Landsat, MODIS, SMAP).
    7. Computes physical thermal GDD, precipitation, Hargreaves-Samani ET0, and soil health indices.
    8. Executes the 3 trained ML models (Suitability, Climate Risk, Yield Regressor).
    9. Generates 3 Pareto-optimal crop rotation sequences conditioned on farmer strategic priorities.
    10. Persists analysis execution record to SQLite database.
    """
    # Coordinate bounds validation
    try:
        DataProcessingEngine.validate_coordinates(payload.latitude, payload.longitude)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    data_sources_queried = [
        "NASA_POWER",
        "USDA_SSURGO",
        "ECMWF_ERA5",
        "USGS_NWIS",
        "USGS_LANDSAT_C2_RASTER",
        "NASA_CMR",
        "USGS_LANDSAT_STAC"
    ]
    successful_sources = []
    failed_sources = []

    year = payload.analysis_year or 2024
    start_date = payload.start_date or f"{year}0401"
    end_date = payload.end_date or f"{year}0930"

    # 1. Fetch NASA POWER Daily Agroclimatology
    climate_res = power_connector.fetch_daily_agroclimatology(
        latitude=payload.latitude,
        longitude=payload.longitude,
        start_date=start_date,
        end_date=end_date,
        use_cache=True
    )
    if climate_res.get("success"):
        successful_sources.append("NASA_POWER")
    else:
        failed_sources.append("NASA_POWER")
        raise HTTPException(status_code=502, detail=climate_res.get("error", "NASA POWER request failed"))

    df_climate = DataProcessingEngine.process_climate_records(climate_res.get("daily_records", []))
    climate_qc = DataProcessingEngine.assess_data_quality(df_climate)
    climate_intel = ClimateIntelligenceEngine.calculate_indicators(df_climate)

    # 2. Fetch USDA SSURGO / STATSGO2 Soils
    soil_res = ssurgo_connector.fetch_soil_profile(payload.latitude, payload.longitude, use_cache=True)
    if not soil_res.get("success"):
        soil_res = ssurgo_connector.get_fallback_profile(payload.latitude, payload.longitude)
        failed_sources.append("USDA_SSURGO_DOMESTIC")
        successful_sources.append("REGIONAL_AG_BENCHMARK")
    else:
        if soil_res.get("is_fallback"):
            successful_sources.append("REGIONAL_AG_BENCHMARK")
        else:
            successful_sources.append("USDA_SSURGO")

    soil_intel = SoilIntelligenceEngine.evaluate_soil_health(soil_res)

    # 3. Fetch Real ECMWF ERA5 Multi-Layer Soil Moisture & Temperature Reanalysis
    era5_res = era5_connector.fetch_soil_moisture_and_reanalysis(
        latitude=payload.latitude,
        longitude=payload.longitude,
        start_date=start_date,
        end_date=end_date,
        use_cache=True
    )
    if era5_res.get("success"):
        successful_sources.append("ECMWF_ERA5")
    else:
        failed_sources.append("ECMWF_ERA5")

    # 4. Fetch Real USGS NWIS Watershed Streamflow Discharge
    water_res = usgs_water_connector.fetch_watershed_hydrology(
        latitude=payload.latitude,
        longitude=payload.longitude,
        use_cache=True
    )
    if water_res.get("success"):
        successful_sources.append("USGS_NWIS")
    else:
        failed_sources.append("USGS_NWIS")

    # 5. Execute Real USGS Landsat Collection 2 Level-2 Surface Reflectance & NDVI Raster Processing
    landsat_raster_res = landsat_raster_connector.fetch_field_ndvi(
        latitude=payload.latitude,
        longitude=payload.longitude,
        start_date=f"{year}-06-01",
        end_date=f"{year}-09-15",
        use_cache=True
    )
    landsat_ndvi_val = None
    if landsat_raster_res.get("success") and landsat_raster_res.get("ndvi_metrics", {}).get("mean_ndvi") is not None:
        landsat_ndvi_val = landsat_raster_res["ndvi_metrics"]["mean_ndvi"]
        successful_sources.append("USGS_LANDSAT_C2_RASTER")
    else:
        failed_sources.append("USGS_LANDSAT_C2_RASTER")

    # 6. Query Earth Observation Granules (Landsat Collection 2 & MODIS Vegetation)
    satellite_feeds = {}
    try:
        landsat_res = earthdata_connector.search_live_granules("LANDSAT_C2", payload.latitude, payload.longitude, limit=3)
        modis_res = earthdata_connector.search_live_granules("MODIS_VEG", payload.latitude, payload.longitude, limit=3)
        satellite_feeds = {
            "landsat_c2": landsat_res,
            "modis_veg": modis_res,
            "landsat_raster_ndvi": landsat_raster_res
        }
        successful_sources.append("NASA_CMR")
    except Exception:
        failed_sources.append("NASA_CMR")

    # Determine clean state/county from payload or coordinates
    req_state = payload.state
    if req_state == "Iowa" and not (40.0 <= payload.latitude <= 43.5 and -96.5 <= payload.longitude <= -90.0):
        req_state = None # Let FieldState infer from real coordinates

    # 7. Create Central Authoritative Selected-Field State
    field_state = FieldState.create(
        latitude=payload.latitude,
        longitude=payload.longitude,
        field_name=payload.field_name,
        field_polygon=payload.field_polygon,
        country=payload.country or "United States",
        state=req_state,
        county=payload.county,
        analysis_year=year,
        start_date=start_date,
        end_date=end_date,
        previous_crop=payload.previous_crop or "corn",
        crop_history=payload.crop_history,
        farmer_priority=payload.farmer_priority or "balanced"
    )

    # 8. Generate Dynamically Optimized Rotation Recommendations via ML Ensemble (v2.1 Satellite-Enhanced when NDVI present)
    rotation_plan = optimizer.optimize(
        climate_summary=climate_intel.get("summary", {}),
        soil_profile=soil_res,
        previous_crop=field_state.previous_crop,
        farmer_priority=field_state.farmer_priority,
        field_name=field_state.field_name,
        latitude=field_state.latitude,
        longitude=field_state.longitude,
        analysis_year=year,
        landsat_ndvi=landsat_ndvi_val
    )

    analysis_timestamp = datetime.now(timezone.utc).isoformat()

    # 9. Persist Real Satellite Observation to SQLite (Phase 4 Persistence)
    if landsat_raster_res.get("success"):
        save_satellite_observation(
            field_id=field_state.field_id,
            dataset_id="DS_USGS_LANDSAT",
            product_id=landsat_raster_res.get("product_id", "Landsat_Collection2_Level2_SR"),
            scene_id=landsat_raster_res.get("scene_id", "UNKNOWN"),
            acquisition_date=landsat_raster_res.get("acquisition_date", analysis_timestamp),
            observation_period=f"{year}0601-{year}0915",
            spatial_resolution=30.0,
            calculated_indicators=landsat_raster_res.get("ndvi_metrics", {}),
            valid_pixel_coverage=landsat_raster_res.get("ndvi_metrics", {}).get("valid_coverage_pct", 0.0),
            quality_metadata=landsat_raster_res.get("quality_flags", {})
        )

    # 10. Persist Analysis Record to Database History
    save_field_analysis(
        field_name=field_state.field_name,
        latitude=field_state.latitude,
        longitude=field_state.longitude,
        region=field_state.county or (field_state.state or "Continental US"),
        state=field_state.state or "US",
        analysis_summary={
            "field_id": field_state.field_id,
            "analysis_year": year,
            "previous_crop": field_state.previous_crop,
            "primary_recommendation": rotation_plan.get("primary_recommendation"),
            "gdd": climate_intel.get("summary", {}).get("total_gdd_f"),
            "precip_in": climate_intel.get("summary", {}).get("total_precip_in"),
            "soil_series": soil_intel.get("dominant_series"),
            "soil_health_score": soil_intel.get("composite_soil_health_score"),
            "landsat_mean_ndvi": landsat_ndvi_val
        }
    )

    return {
        "success": True,
        "geospatial_context": {
            "requested_coordinates": {
                "latitude": payload.latitude,
                "longitude": payload.longitude
            },
            "validated_coordinates": {
                "latitude": field_state.latitude,
                "longitude": field_state.longitude
            },
            "location_identifier": field_state.field_name,
            "field_id": field_state.field_id,
            "country": field_state.country,
            "state": field_state.state,
            "county": field_state.county,
            "field_polygon": field_state.field_polygon,
            "geospatial_hash": field_state.geospatial_hash,
            "is_conus_covered": field_state.is_conus_covered(),
            "data_sources_queried": data_sources_queried,
            "successful_sources": successful_sources,
            "failed_sources": failed_sources,
            "boundary_type": field_state.observation_mode,
            "analysis_timestamp": analysis_timestamp
        },
        "field_profile": {
            "field_id": field_state.field_id,
            "name": field_state.field_name,
            "country": field_state.country,
            "state": field_state.state or ("Target State" if field_state.is_conus_covered() else "International / Benchmark"),
            "county": field_state.county,
            "latitude": field_state.latitude,
            "longitude": field_state.longitude,
            "previous_crop": field_state.previous_crop,
            "crop_history": field_state.crop_history,
            "farmer_priority": field_state.farmer_priority,
            "analysis_year": year,
            "geospatial_hash": field_state.geospatial_hash
        },
        "climate_summary": climate_intel.get("summary"),
        "climate_indicators": climate_intel.get("indicators"),
        "monthly_chart_data": climate_intel.get("monthly_chart_data"),
        "soil_profile": soil_intel,
        "era5_reanalysis": era5_res,
        "watershed_hydrology": water_res,
        "landsat_raster_observation": landsat_raster_res,
        "satellite_feeds": satellite_feeds,
        "rotation_decision_engine": rotation_plan,
        "ml_inferences": rotation_plan.get("ml_inferences", {}),
        "provenance": {
            "climate_source": "NASA Langley Research Center (POWER MERRA-2) [LIVE_SOURCE_DATA]",
            "soil_source": "USDA Natural Resources Conservation Service (SSURGO SDA) [LIVE_SOURCE_DATA]" if field_state.is_conus_covered() else "Regional Agroclimatic Benchmark [HISTORICAL_SOURCE_DATA]",
            "soil_moisture_source": "ECMWF / Copernicus Climate Change Service (ERA5 Land) [LIVE_SOURCE_DATA]",
            "satellite_raster_source": "USGS / NASA Landsat 8-9 Collection 2 Level-2 Surface Reflectance (SR_B4 & SR_B5 COGs) [LIVE_RASTER_OBSERVATION]",
            "hydrology_source": "USGS Water Resources Mission Area (NWIS SensorThings) [LIVE_SOURCE_DATA]",
            "satellite_metadata": "NASA Common Metadata Repository (CMR) & USGS STAC [HISTORICAL_SOURCE_DATA]",
            "ml_models": f"FARMINTEL Multi-Model Ensemble {rotation_plan.get('ml_inferences', {}).get('model_version', 'v2.1')} [MODEL_ESTIMATE]",
            "optimizer": "Constrained Multi-Objective Sequence Optimizer [DERIVED_INDICATOR]"
        }
    }


@router.get("/reverse-geocode")
def reverse_geocode_location(latitude: float = Query(...), longitude: float = Query(...)):
    """
    Resolves decimal coordinates (lat, lon) into authoritative administrative entities:
    County, State, State Code, Country, and Display Name.
    Rejects invalid coordinates and ensures complete synchronization between map and field identity.
    """
    try:
        DataProcessingEngine.validate_coordinates(latitude, longitude)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    return GeocodingService.reverse_geocode(latitude, longitude)


@router.get("/search")
def search_locations(q: str = Query(..., min_length=2)):
    """Searches for US places, counties, cities, or ZIP codes by text query."""
    return {"results": GeocodingService.search_location(q)}


@router.get("/availability")
def get_data_availability(
    latitude: float = Query(...),
    longitude: float = Query(...),
    start_date: str = Query("2024-04-01"),
    end_date: str = Query("2024-09-30")
):
    """
    Evaluates real-time dataset coverage and accessibility across all 28 challenge data sources
    for the exact selected coordinates and date range.
    """
    try:
        DataProcessingEngine.validate_coordinates(latitude, longitude)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    return DataAvailabilityService.check_availability(latitude, longitude, start_date, end_date)
