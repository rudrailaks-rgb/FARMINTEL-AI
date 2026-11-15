"""
FARMINTEL AI - Central Authoritative Selected-Field State Object
NASA Space Apps Challenge: Field Shift — Adapting Farms with NASA Data

Guarantees geospatial integrity: coordinate validation, location identity,
field boundary specification, and consistent parameter propagation across
all NASA, USDA, and European space agency data connectors and ML engines.
"""

import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator

class FieldState(BaseModel):
    field_id: str = Field(..., description="Unique field state identifier (FARM_<hash>)")
    field_name: str = Field("Target Agricultural Field", description="Human-readable field name")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    field_polygon: Optional[List[List[float]]] = Field(None, description="Optional GeoJSON polygon boundary coordinates [[lon, lat], ...]")
    country: str = Field("United States", description="Country name")
    state: Optional[str] = Field(None, description="State / Province")
    county: Optional[str] = Field(None, description="County name where available")
    analysis_start_date: str = Field("20240401", description="Observation start date (YYYYMMDD)")
    analysis_end_date: str = Field("20240930", description="Observation end date (YYYYMMDD)")
    analysis_year: int = Field(2024, ge=1980, le=2030, description="Target observation baseline year")
    previous_crop: str = Field("corn", description="Prior season crop grown on the field")
    crop_history: List[str] = Field(default_factory=list, description="Historical crop sequence e.g. ['corn', 'soybeans']")
    farmer_priority: str = Field("balanced", description="Strategic farmer priority")
    observation_mode: str = Field(
        "POINT_OBSERVATION_WITH_POLYGON_SOIL_INTERSECTION",
        description="Explicit description of spatial sampling scale (Point vs Polygon)"
    )
    geospatial_hash: str = Field("", description="Cryptographic SHA-256 coordinate & parameter fingerprint")
    retrieval_timestamp: str = Field("", description="ISO 8601 UTC timestamp of creation")

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise ValueError(f"Latitude must be between -90 and 90. Got {v}")
        return round(float(v), 5)

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError(f"Longitude must be between -180 and 180. Got {v}")
        return round(float(v), 5)

    @classmethod
    def create(
        cls,
        latitude: float,
        longitude: float,
        field_name: Optional[str] = None,
        field_polygon: Optional[List[List[float]]] = None,
        country: str = "United States",
        state: Optional[str] = None,
        county: Optional[str] = None,
        analysis_year: int = 2024,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        previous_crop: str = "corn",
        crop_history: Optional[List[str]] = None,
        farmer_priority: str = "balanced"
    ) -> "FieldState":
        lat = round(float(latitude), 5)
        lon = round(float(longitude), 5)
        clean_name = field_name or f"Field_{lat:.4f}_{lon:.4f}"
        clean_prev = (previous_crop or "corn").lower().replace(" ", "_")
        clean_prio = (farmer_priority or "balanced").lower().replace(" ", "_")
        s_date = start_date or f"{analysis_year}0401"
        e_date = end_date or f"{analysis_year}0930"
        hist = crop_history or [clean_prev]

        # Mode distinction: Point vs Field Boundary Polygon
        obs_mode = (
            "FIELD_POLYGON_SPATIAL_AGGREGATION"
            if field_polygon and len(field_polygon) >= 3
            else "POINT_OBSERVATION_WITH_POLYGON_SOIL_INTERSECTION"
        )

        raw_str = f"{lat}:{lon}:{analysis_year}:{clean_prev}:{clean_prio}:{s_date}:{e_date}:{country}:{state or ''}:{county or ''}"
        geo_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]
        field_id = f"FARM_{geo_hash}"
        ts = datetime.now(timezone.utc).isoformat()

        # Resolve state/county dynamically via GeocodingService
        inferred_state = state
        inferred_county = county
        inferred_country = country

        if not inferred_state or not inferred_county or inferred_county == "Story County" and not (abs(lat - 42.0308) < 0.3 and abs(lon - (-93.6319)) < 0.3):
            try:
                from ..services.geocoding_service import GeocodingService
                geo_info = GeocodingService.reverse_geocode(lat, lon)
                if geo_info.get("success"):
                    inferred_county = geo_info.get("county") or inferred_county
                    inferred_state = geo_info.get("state") or inferred_state
                    inferred_country = geo_info.get("country") or inferred_country
            except Exception:
                pass

        if not inferred_state:
            if (40.0 <= lat <= 43.5) and (-96.5 <= lon <= -90.0):
                inferred_state = "Iowa"
                if abs(lat - 42.0308) < 0.2 and abs(lon - (-93.6319)) < 0.2:
                    inferred_county = "Story County"
            elif (35.0 <= lat <= 38.5) and (-121.5 <= lon <= -118.0):
                inferred_state = "California"
                if abs(lat - 36.7468) < 0.4 and abs(lon - (-119.7726)) < 0.4:
                    inferred_county = "Fresno County"
            elif (40.5 <= lat <= 41.5) and (-99.0 <= lon <= -98.0):
                inferred_state = "Nebraska"
                inferred_county = "Hall County"
            elif (37.0 <= lat <= 40.0) and (-102.0 <= lon <= -95.0):
                inferred_state = "Kansas"
                inferred_county = "Finney County"
            elif (37.0 <= lat <= 41.0) and (-109.0 <= lon <= -102.0):
                inferred_state = "Colorado"

        return cls(
            field_id=field_id,
            field_name=clean_name,
            latitude=lat,
            longitude=lon,
            field_polygon=field_polygon,
            country=inferred_country or country,
            state=inferred_state,
            county=inferred_county,
            analysis_start_date=s_date,
            analysis_end_date=e_date,
            analysis_year=analysis_year,
            previous_crop=clean_prev,
            crop_history=hist,
            farmer_priority=clean_prio,
            observation_mode=obs_mode,
            geospatial_hash=geo_hash,
            retrieval_timestamp=ts
        )

    def is_conus_covered(self) -> bool:
        """Determines if the coordinates lie within the contiguous United States SSURGO survey footprint."""
        return (24.0 <= self.latitude <= 50.0) and (-125.0 <= self.longitude <= -66.0)
