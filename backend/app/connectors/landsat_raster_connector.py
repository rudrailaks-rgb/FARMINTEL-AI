"""
FARMINTEL AI - Landsat Collection 2 Level-2 Surface Reflectance & NDVI Engine
Source: USGS / NASA Landsat 8-9 Collection 2 Level-2 Surface Reflectance (Operational Land Imager)
Protocols: STAC API & Cloud-Optimized GeoTIFF (COG) HTTP Range Requests via Planetary Computer
Scale & Offset: Reflectance = DN * 0.0000275 - 0.2 (USGS Collection 2 Specification)
Quality Bitmasks: QA_PIXEL bit 0 (fill), bit 1 (dilated cloud), bit 3 (cloud), bit 4 (cloud shadow)
"""

from typing import Dict, Any, List, Optional, Tuple
import os
import time
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from pyproj import Transformer
import pystac_client
import planetary_computer as pc
from .base import BaseConnector
from ..database import generate_cache_key, get_cached_response, set_cached_response, save_satellite_observation

class LandsatRasterConnector(BaseConnector):
    STAC_ENDPOINT = "https://planetarycomputer.microsoft.com/api/stac/v1"
    COLLECTION_ID = "landsat-c2-l2"
    SCALE_FACTOR = 0.0000275
    ADD_OFFSET = -0.20

    def __init__(self):
        super().__init__(
            source_name="USGS_LANDSAT_C2",
            base_url=self.STAC_ENDPOINT,
            default_timeout=30
        )
        self._stac_client = None

    def _get_client(self) -> pystac_client.Client:
        if self._stac_client is None:
            self._stac_client = pystac_client.Client.open(
                self.STAC_ENDPOINT,
                modifier=pc.sign_inplace
            )
        return self._stac_client

    def fetch_field_ndvi(
        self,
        latitude: float,
        longitude: float,
        start_date: str = "2024-06-01",
        end_date: str = "2024-09-15",
        max_cloud_cover: float = 25.0,
        buffer_meters: float = 300.0,
        field_polygon: Optional[List[List[float]]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Retrieves real USGS Landsat Collection 2 Level-2 Red (B4) and NIR (B5) pixels
        using COG HTTP range requests and computes field-level NDVI and QA coverage.
        """
        # Format dates to ISO
        s_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}" if len(start_date) == 8 and "-" not in start_date else start_date
        e_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}" if len(end_date) == 8 and "-" not in end_date else end_date

        cache_params = {
            "lat": round(latitude, 4),
            "lon": round(longitude, 4),
            "start": s_date,
            "end": e_date,
            "cloud": max_cloud_cover,
            "buf": buffer_meters
        }
        cache_key = generate_cache_key(self.source_name, self.STAC_ENDPOINT, cache_params)

        if use_cache:
            cached = get_cached_response(cache_key)
            if cached:
                return {**cached, "cached": True}

        t0 = time.time()
        client = self._get_client()

        # STAC spatial discovery
        search = client.search(
            collections=[self.COLLECTION_ID],
            intersects={"type": "Point", "coordinates": [longitude, latitude]},
            datetime=f"{s_date}/{e_date}",
            query={"eo:cloud_cover": {"lt": max_cloud_cover}},
            sortby=[{"field": "properties.eo:cloud_cover", "direction": "asc"}],
            max_items=3
        )

        items = list(search.items())
        if not items:
            # Fallback: search broader window or return clean missing-data state
            return {
                "success": False,
                "error": "No clear Landsat Collection 2 scene found under cloud threshold",
                "coordinates": {"latitude": latitude, "longitude": longitude},
                "observation_window": {"start": s_date, "end": e_date},
                "status": "NO_CLEAR_SCENE_AVAILABLE"
            }

        # Select best clear scene
        best_item = items[0]
        scene_id = best_item.id
        acq_datetime = best_item.datetime.isoformat() if best_item.datetime else str(best_item.properties.get("datetime"))
        cloud_pct = float(best_item.properties.get("eo:cloud_cover", 0.0))
        platform = best_item.properties.get("platform", "Landsat")

        # Extract signed asset URLs
        red_asset = best_item.assets.get("red")
        nir_asset = best_item.assets.get("nir08")
        qa_asset = best_item.assets.get("qa_pixel")

        if not (red_asset and nir_asset and qa_asset):
            return {
                "success": False,
                "error": "Required spectral band assets missing from STAC item",
                "scene_id": scene_id
            }

        red_href = red_asset.href
        nir_href = nir_asset.href
        qa_href = qa_asset.href

        try:
            # Open COGs with rasterio (HTTP range requests fetch only the window)
            with rasterio.open(red_href) as src_red, \
                 rasterio.open(nir_href) as src_nir, \
                 rasterio.open(qa_href) as src_qa:

                crs_str = str(src_red.crs)
                res_tuple = src_red.res

                # Transform coordinates to raster projection (e.g. UTM)
                transformer = Transformer.from_crs("EPSG:4326", src_red.crs, always_xy=True)
                x_proj, y_proj = transformer.transform(longitude, latitude)

                # Define field bounding window
                win = from_bounds(
                    x_proj - buffer_meters,
                    y_proj - buffer_meters,
                    x_proj + buffer_meters,
                    y_proj + buffer_meters,
                    src_red.transform
                )

                # Read only window pixels across bands
                red_raw = src_red.read(1, window=win)
                nir_raw = src_nir.read(1, window=win)
                qa_raw = src_qa.read(1, window=win)

                total_pixels = int(red_raw.size)
                if total_pixels == 0:
                    return {
                        "success": False,
                        "error": "Extracted spatial window contains 0 pixels",
                        "scene_id": scene_id
                    }

                # Apply official USGS Surface Reflectance scaling
                # Reflectance = (DN * 0.0000275) - 0.2
                red_refl = np.where(red_raw > 0, red_raw * self.SCALE_FACTOR + self.ADD_OFFSET, np.nan)
                nir_refl = np.where(nir_raw > 0, nir_raw * self.SCALE_FACTOR + self.ADD_OFFSET, np.nan)

                # Apply USGS QA_PIXEL Bitmasks:
                # Bit 0 = Fill
                # Bit 1 = Dilated Cloud
                # Bit 3 = Cloud
                # Bit 4 = Cloud Shadow
                # Bit 5 = Snow
                fill_mask = (qa_raw & (1 << 0)) != 0
                dilated_cloud = (qa_raw & (1 << 1)) != 0
                cloud_mask = (qa_raw & (1 << 3)) != 0
                shadow_mask = (qa_raw & (1 << 4)) != 0
                snow_mask = (qa_raw & (1 << 5)) != 0

                qa_invalid = fill_mask | dilated_cloud | cloud_mask | shadow_mask | snow_mask
                math_invalid = np.isnan(red_refl) | np.isnan(nir_refl) | (red_refl <= 0) | (nir_refl <= 0)
                invalid_mask = qa_invalid | math_invalid

                # NDVI = (NIR - Red) / (NIR + Red)
                denom = nir_refl + red_refl
                ndvi_grid = np.where((~invalid_mask) & (denom > 0), (nir_refl - red_refl) / denom, np.nan)

                # Filter valid physical range [-1.0, 1.0]
                valid_mask = (~np.isnan(ndvi_grid)) & (ndvi_grid >= -1.0) & (ndvi_grid <= 1.0)
                valid_pixels = ndvi_grid[valid_mask]
                valid_count = int(len(valid_pixels))
                coverage_pct = round((valid_count / total_pixels) * 100.0, 1)

                if valid_count == 0:
                    mean_ndvi = None
                    median_ndvi = None
                    min_ndvi = None
                    max_ndvi = None
                    p25_ndvi = None
                    p75_ndvi = None
                    vigor_status = "CLOUD_OBSCURED"
                else:
                    mean_ndvi = round(float(np.mean(valid_pixels)), 4)
                    median_ndvi = round(float(np.median(valid_pixels)), 4)
                    min_ndvi = round(float(np.min(valid_pixels)), 4)
                    max_ndvi = round(float(np.max(valid_pixels)), 4)
                    p25_ndvi = round(float(np.percentile(valid_pixels, 25)), 4)
                    p75_ndvi = round(float(np.percentile(valid_pixels, 75)), 4)

                    if mean_ndvi >= 0.70:
                        vigor_status = "VERY_HIGH_CANOPY_VIGOR"
                    elif mean_ndvi >= 0.50:
                        vigor_status = "HIGH_CANOPY_VIGOR"
                    elif mean_ndvi >= 0.35:
                        vigor_status = "MODERATE_CANOPY_VIGOR"
                    elif mean_ndvi >= 0.20:
                        vigor_status = "LOW_EMERGENCE_OR_RESIDUE"
                    else:
                        vigor_status = "BARE_SOIL_OR_FALLOW"

                latency = round(time.time() - t0, 2)

                res = {
                    "success": True,
                    "dataset_id": "DS_USGS_LANDSAT",
                    "product_id": "Landsat_Collection2_Level2_SR",
                    "scene_id": scene_id,
                    "platform": platform,
                    "acquisition_date": acq_datetime,
                    "coordinates": {"latitude": latitude, "longitude": longitude},
                    "raster_metadata": {
                        "crs": crs_str,
                        "spatial_resolution_m": 30.0,
                        "full_scene_dimensions": f"{src_red.width}x{src_red.height}",
                        "sampling_window": f"{red_raw.shape[0]}x{red_raw.shape[1]} pixels ({buffer_meters*2:.0f}m x {buffer_meters*2:.0f}m)"
                    },
                    "scene_cloud_cover_pct": cloud_pct,
                    "ndvi_metrics": {
                        "mean_ndvi": mean_ndvi,
                        "median_ndvi": median_ndvi,
                        "min_ndvi": min_ndvi,
                        "max_ndvi": max_ndvi,
                        "iqr_range": [p25_ndvi, p75_ndvi] if p25_ndvi is not None else None,
                        "canopy_vigor_classification": vigor_status,
                        "valid_pixel_count": valid_count,
                        "total_window_pixels": total_pixels,
                        "valid_coverage_pct": coverage_pct
                    },
                    "sample_matrix_3x3": np.round(ndvi_grid[:3, :3], 3).tolist(),
                    "quality_flags": {
                        "cloud_contaminated": bool(cloud_mask.any()),
                        "shadow_contaminated": bool(shadow_mask.any()),
                        "fill_pixels_present": bool(fill_mask.any()),
                        "passed_usgs_qa_audit": bool(coverage_pct >= 50.0)
                    },
                    "latency_sec": latency,
                    "provenance": {
                        "agency": "USGS / NASA Earth Resources Observation and Science (EROS)",
                        "collection": "Landsat Collection 2 Level-2 Surface Reflectance",
                        "bands_processed": ["SR_B4 (Red)", "SR_B5 (NIR)", "QA_PIXEL"],
                        "scale_equation": "Reflectance = DN * 0.0000275 - 0.2",
                        "ndvi_equation": "NDVI = (NIR - Red) / (NIR + Red)",
                        "cog_access": "Public Cloud-Optimized GeoTIFF Range Requests"
                    }
                }

                if use_cache and valid_count > 0:
                    set_cached_response(cache_key, self.source_name, self.STAC_ENDPOINT, cache_params, res)

                return res

        except Exception as e:
            return {
                "success": False,
                "error": f"Landsat raster extraction error: {str(e)}",
                "scene_id": scene_id,
                "latency_sec": round(time.time() - t0, 2)
            }
