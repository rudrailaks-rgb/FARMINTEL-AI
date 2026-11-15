"""
FARMINTEL AI - Application Configuration & Environment Settings
"""

import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "data" / "cache"
DB_PATH = BASE_DIR / "data" / "farmintel.db"

class Settings(BaseModel):
    PROJECT_NAME: str = "FARMINTEL AI"
    TAGLINE: str = "Intelligence for Every Acre"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    CORS_ORIGINS: list[str] = [
        origin.strip().rstrip("/")
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]
    
    # NASA APIs
    NASA_POWER_BASE_URL: str = "https://power.larc.nasa.gov/api/temporal/daily/point"
    NASA_CMR_SEARCH_URL: str = "https://cmr.earthdata.nasa.gov/search/granules.json"
    EARTHDATA_USERNAME: str = os.getenv("EARTHDATA_USERNAME", "")
    EARTHDATA_PASSWORD: str = os.getenv("EARTHDATA_PASSWORD", "")
    EARTHDATA_TOKEN: str = os.getenv("EARTHDATA_TOKEN", "")
    
    # USDA APIs
    USDA_SDA_POST_URL: str = "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest"
    USDA_NASS_API_KEY: str = os.getenv("USDA_NASS_API_KEY", "")
    
    # Database and Caching
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH") or str(DB_PATH)
    CACHE_DIR_PATH: str = os.getenv("CACHE_DIR_PATH") or str(CACHE_DIR)
    CACHE_TTL_DAYS: int = 7
    
    # Default Pilot Region: Story County, Ames, Iowa (Midwest Corn Belt)
    DEFAULT_LATITUDE: float = 42.0308
    DEFAULT_LONGITUDE: float = -93.6319
    DEFAULT_REGION_NAME: str = "Story County, Iowa (Midwest Corn Belt)"

settings = Settings()

if "*" in settings.CORS_ORIGINS:
    raise ValueError("CORS_ORIGINS must contain explicit origins, not '*'.")

Path(settings.SQLITE_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
Path(settings.CACHE_DIR_PATH).mkdir(parents=True, exist_ok=True)
