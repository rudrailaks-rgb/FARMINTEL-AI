"""
FARMINTEL AI - Dataset Registry API Routes
"""

from fastapi import APIRouter, HTTPException
from ..connectors.registry import DataSourceRegistry
from ..connectors.official_registry import OFFICIAL_DATA_SOURCES
from ..models.schemas import TestConnectionRequest

router = APIRouter(prefix="/api/datasets", tags=["Dataset Registry"])
registry = DataSourceRegistry()

@router.get("")
def list_datasets():
    """Lists all integrated NASA and USDA datasets with their tracking metadata."""
    return {
        "success": True,
        "count": len(OFFICIAL_DATA_SOURCES),
        "datasets": OFFICIAL_DATA_SOURCES
    }

@router.get("/registry")
def get_official_registry():
    """Returns the official 28-dataset registry covering all challenge data sources."""
    return {
        "success": True,
        "count": len(OFFICIAL_DATA_SOURCES),
        "datasets": OFFICIAL_DATA_SOURCES
    }

@router.get("/status")
def get_dataset_statuses():
    """Returns the live connection health and status summary of all data sources."""
    return registry.run_health_check_all()

@router.post("/test-connection")
def test_dataset_connection(payload: TestConnectionRequest):
    """Executes an active test query against a specific dataset provider."""
    res = registry.test_connection(payload.dataset_id, payload.latitude, payload.longitude)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Connection test failed"))
    return res

