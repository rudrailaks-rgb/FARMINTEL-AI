"""
FARMINTEL AI - Pydantic Request & Response Data Models
Guarantees strict bounds validation on all geographic and agronomic parameters.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator

class HealthResponse(BaseModel):
    status: str
    project: str
    version: str
    timestamp: str

class LocationRequest(BaseModel):
    latitude: float = Field(..., description="Latitude in decimal degrees (-90 to 90)")
    longitude: float = Field(..., description="Longitude in decimal degrees (-180 to 180)")
    field_name: Optional[str] = "Midwest Field 1"
    state: Optional[str] = None

    @field_validator("latitude")
    @classmethod
    def check_lat(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise ValueError(f"Latitude must be between -90.0 and +90.0 degrees. Received: {v}")
        return round(float(v), 5)

    @field_validator("longitude")
    @classmethod
    def check_lon(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError(f"Longitude must be between -180.0 and +180.0 degrees. Received: {v}")
        return round(float(v), 5)

class ClimateFetchRequest(BaseModel):
    latitude: float = Field(42.0308, ge=-90.0, le=90.0)
    longitude: float = Field(-93.6319, ge=-180.0, le=180.0)
    start_date: str = Field("20240401", description="Format: YYYYMMDD")
    end_date: str = Field("20240930", description="Format: YYYYMMDD")
    use_cache: bool = True

class TestConnectionRequest(BaseModel):
    dataset_id: str
    latitude: Optional[float] = 42.0308
    longitude: Optional[float] = -93.6319

class FieldAnalysisRequest(BaseModel):
    latitude: float = Field(..., description="Latitude in decimal degrees (-90 to 90)")
    longitude: float = Field(..., description="Longitude in decimal degrees (-180 to 180)")
    field_name: Optional[str] = None
    country: Optional[str] = "United States"
    state: Optional[str] = None
    county: Optional[str] = None
    field_polygon: Optional[List[List[float]]] = None
    previous_crop: Optional[str] = "corn"
    crop_history: Optional[List[str]] = None
    farmer_priority: Optional[str] = "balanced" # 'balanced', 'soil_health', 'drought_resilience', 'profit'
    analysis_year: Optional[int] = 2024
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    @field_validator("latitude")
    @classmethod
    def check_lat(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise ValueError(f"Latitude must be between -90.0 and +90.0 degrees. Received: {v}")
        return round(float(v), 5)

    @field_validator("longitude")
    @classmethod
    def check_lon(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError(f"Longitude must be between -180.0 and +180.0 degrees. Received: {v}")
        return round(float(v), 5)

class RotationCompareRequest(BaseModel):
    latitude: float = Field(42.0308, ge=-90.0, le=90.0)
    longitude: float = Field(-93.6319, ge=-180.0, le=180.0)
    field_name: Optional[str] = "Midwest Field"
    state: Optional[str] = None
    previous_crop: Optional[str] = "corn"
    farmer_priority: Optional[str] = "balanced"
    analysis_year: Optional[int] = 2024
