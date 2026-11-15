"""
FARMINTEL AI - NASA Earth Observation Satellite Data Connectors
Integrates NASA SMAP, GPM IMERG, MODIS, Landsat Collection 2, ECOSTRESS, SRTM, and GRACE.
Uses NASA Common Metadata Repository (CMR) Search API and USGS STAC endpoints.
"""

from typing import Dict, Any, List, Optional
import requests
from .base import BaseConnector
from ..config import settings

class NasaEarthdataConnector(BaseConnector):
    PRODUCTS = {
        "SMAP": {
            "name": "NASA SMAP Soil Moisture",
            "concept_id": "C2938664763-NSIDC_CPRD",
            "short_name": "SPL3SMP_E",
            "version": "006",
            "spatial_resolution": "9 km x 9 km EASE-Grid 2.0",
            "temporal_resolution": "Daily",
            "measurement_depth": "Surface (0-5 cm); Root-zone via SPL4SMGP (0-100 cm)",
            "units": "m³/m³ (volumetric)",
            "daac": "NSIDC DAAC",
            "official_url": "https://nsidc.org/data/smap",
            "auth_required": True
        },
        "GPM_IMERG": {
            "name": "NASA GPM IMERG Final Precipitation",
            "concept_id": "C2723754864-GES_DISC",
            "short_name": "GPM_3IMERGDF",
            "version": "07",
            "spatial_resolution": "0.1° x 0.1° (~10 km)",
            "temporal_resolution": "Daily accumulation",
            "measurement_depth": "Surface atmospheric column",
            "units": "mm/day",
            "daac": "GES DISC",
            "official_url": "https://gpm.nasa.gov/data/imerg",
            "auth_required": True
        },
        "MODIS_VEG": {
            "name": "NASA MODIS Terra Vegetation Indices",
            "concept_id": "C1711961230-LPDAAC_ECS",
            "short_name": "MOD13Q1",
            "version": "061",
            "spatial_resolution": "250 m x 250 m (Sinusoidal)",
            "temporal_resolution": "16-day Composite",
            "measurement_depth": "Canopy surface reflectance",
            "units": "Normalized Index (-1.0 to 1.0)",
            "daac": "LP DAAC",
            "official_url": "https://doi.org/10.5067/MODIS/MOD13Q1.061",
            "auth_required": True
        },
        "LANDSAT_C2": {
            "name": "USGS/NASA Landsat 8-9 Collection 2 Surface Reflectance",
            "short_name": "LC08_L2SP / LC09_L2SP",
            "version": "Collection 2 Level 2",
            "spatial_resolution": "30 m x 30 m",
            "temporal_resolution": "8–16 days repeat",
            "measurement_depth": "Field-scale surface reflectance",
            "units": "Surface Reflectance",
            "daac": "USGS EROS / NASA LP DAAC",
            "official_url": "https://www.usgs.gov/landsat-missions/landsat-data-access",
            "auth_required": False
        },
        "ECOSTRESS": {
            "name": "NASA ECOSTRESS Evapotranspiration & PT-JPL Water Stress",
            "concept_id": "C2076092040-LPCLOUD",
            "short_name": "ECO3ETPTJPL",
            "version": "002",
            "spatial_resolution": "70 m x 70 m",
            "temporal_resolution": "Variable (ISS orbit 1-5 days)",
            "measurement_depth": "Evaporative fraction & canopy thermal state",
            "units": "W/m² and Evaporative Stress Index (0-1)",
            "daac": "LP DAAC Cloud",
            "official_url": "https://ecostress.jpl.nasa.gov/data/",
            "auth_required": True
        },
        "SRTM_DEM": {
            "name": "NASA Shuttle Radar Topography Mission (SRTM) Global 1-arcsecond",
            "concept_id": "C1000000240-LPDAAC_ECS",
            "short_name": "SRTMGL1",
            "version": "003",
            "spatial_resolution": "30 m x 30 m (1 arc-second)",
            "temporal_resolution": "Static digital elevation model",
            "measurement_depth": "Terrain surface elevation",
            "units": "Meters AMSL",
            "daac": "LP DAAC",
            "official_url": "https://search.earthdata.nasa.gov/",
            "auth_required": False
        },
        "GRACE_FO": {
            "name": "NASA GRACE / GRACE-FO Terrestrial Water Storage Anomaly",
            "concept_id": "C1994646549-PO_DAAC",
            "short_name": "TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.1_V3",
            "version": "RL06.1",
            "spatial_resolution": "0.5° x 0.5° (Mascon resolution ~300 km)",
            "temporal_resolution": "Monthly",
            "measurement_depth": "Deep aquifer & regional groundwater column",
            "units": "Equivalent Water Thickness (cm anomaly)",
            "daac": "PO DAAC",
            "official_url": "https://grace.jpl.nasa.gov/",
            "auth_required": False
        }
    }

    def __init__(self):
        super().__init__(
            source_name="NASA_EARTHDATA",
            base_url=settings.NASA_CMR_SEARCH_URL,
            default_timeout=25
        )

    def search_live_granules(
        self,
        product_key: str,
        latitude: float,
        longitude: float,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Queries NASA CMR Search API for recent granules covering the target coordinate.
        Does not require Earthdata login for metadata search.
        """
        if product_key not in self.PRODUCTS:
            return {"success": False, "error": f"Unknown product: {product_key}"}

        prod = self.PRODUCTS[product_key]
        short_name = prod.get("short_name", "").split()[0].split("/")[0]

        params = {
            "short_name": short_name,
            "point": f"{longitude},{latitude}",
            "page_size": limit,
            "sort_key": "-start_date"
        }

        try:
            resp = self.session.get(self.base_url, params=params, timeout=self.default_timeout)
            if resp.status_code == 200:
                data = resp.json()
                entries = data.get("feed", {}).get("entry", [])
                granules = []
                for e in entries:
                    links = [l.get("href") for l in e.get("links", []) if l.get("href", "").endswith((".h5", ".nc4", ".tif", ".hdf"))]
                    granules.append({
                        "title": e.get("title"),
                        "granule_size_mb": e.get("granule_size"),
                        "time_start": e.get("time_start"),
                        "time_end": e.get("time_end"),
                        "direct_download_url": links[0] if links else None
                    })
                return {
                    "success": True,
                    "product": prod["name"],
                    "short_name": short_name,
                    "spatial_resolution": prod["spatial_resolution"],
                    "temporal_resolution": prod["temporal_resolution"],
                    "measurement_depth": prod["measurement_depth"],
                    "units": prod["units"],
                    "granules_found": len(granules),
                    "granules": granules,
                    "auth_required": prod["auth_required"],
                    "provenance": {
                        "daac": prod["daac"],
                        "official_url": prod["official_url"],
                        "cmr_endpoint": resp.url
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"CMR Search HTTP {resp.status_code}: {resp.text[:200]}",
                    "product": prod["name"]
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"CMR query failed: {str(e)}",
                "product": prod["name"]
            }

    def get_all_products_metadata(self) -> Dict[str, Any]:
        return self.PRODUCTS
