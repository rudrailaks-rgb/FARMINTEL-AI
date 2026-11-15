"""
FARMINTEL AI - Main Application Entrypoint
NASA Space Apps Challenge 2026: Field Shift — Adapting Farms with NASA Data
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone
import os
from .config import settings
from .api.routes_datasets import router as datasets_router
from .api.routes_climate import router as climate_router
from .api.routes_soil import router as soil_router
from .api.routes_crops import router as crops_router
from .api.routes_field import router as field_router
from .api.routes_rotation import router as rotation_router
from .api.routes_ml import router as ml_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "FARMINTEL AI is an uncertainty-aware, explainable agricultural decision support system. "
        "It integrates real NASA Earth observation data (NASA POWER, SMAP, GPM, MODIS, Landsat) "
        "and USDA NRCS SSURGO edaphic profiles to evaluate multi-year crop rotation strategies "
        "across the United States."
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Custom Exception Handler ensuring clean, human-readable errors (eliminates [object Object])
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field_loc = err.get("loc", [])
        field_name = field_loc[-1] if field_loc else "parameter"
        msg = err.get("msg", "Invalid value")
        errors.append(f"Field '{field_name}': {msg}")
    clean_msg = "; ".join(errors) or "Invalid request parameters"
    return JSONResponse(
        status_code=400,
        content={"detail": clean_msg, "error_type": "VALIDATION_ERROR"}
    )

# Enable CORS for local React/Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Sub-Routers
app.include_router(datasets_router)
app.include_router(climate_router)
app.include_router(soil_router)
app.include_router(crops_router)
app.include_router(field_router)
app.include_router(rotation_router)
app.include_router(ml_router)

@app.get("/api/health", tags=["System Health"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "HEALTHY",
        "project": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pilot_region": settings.DEFAULT_REGION_NAME,
        "default_coordinates": {
            "latitude": settings.DEFAULT_LATITUDE,
            "longitude": settings.DEFAULT_LONGITUDE
        }
    }

# Mount production frontend build if present
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
