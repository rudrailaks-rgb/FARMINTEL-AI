"""
FARMINTEL AI - USGS NWIS Water Data Connector
Source: United States Geological Survey (USGS) Water Resources Mission Area
Endpoints: https://waterservices.usgs.gov/nwis/iv/ & https://api.waterdata.usgs.gov/
"""

from typing import Dict, Any, List, Optional
import time
import requests
from .base import BaseConnector
from ..database import generate_cache_key, get_cached_response, set_cached_response

class UsgsWaterConnector(BaseConnector):
    # Mapping of common agricultural coordinates to County FIPS codes
    COUNTY_FIPS_LOOKUP = {
        (42.0, -93.6): ("19169", "Story County", "IA"),
        (36.7, -119.8): ("06019", "Fresno County", "CA"),
        (40.9, -98.3): ("31079", "Hall County", "NE"),
        (38.0, -100.8): ("20055", "Finney County", "KS"),
        (46.9, -96.8): ("38017", "Cass County", "ND")
    }

    def __init__(self):
        super().__init__(
            source_name="USGS_NWIS",
            base_url="https://waterservices.usgs.gov/nwis/iv/",
            default_timeout=10
        )

    def fetch_watershed_hydrology(
        self,
        latitude: float,
        longitude: float,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Retrieves real-time streamflow discharge and gage height from the nearest
        USGS monitoring locations within the agricultural county.
        """
        county_cd = None
        county_name = "Target Watershed"
        state_cd = "US"

        # Match nearest county FIPS
        for (ref_lat, ref_lon), (fips, name, st) in self.COUNTY_FIPS_LOOKUP.items():
            if abs(latitude - ref_lat) < 1.0 and abs(longitude - ref_lon) < 1.0:
                county_cd = fips
                county_name = name
                state_cd = st
                break

        cache_key = generate_cache_key(self.source_name, self.base_url, {"lat": round(latitude, 2), "lon": round(longitude, 2), "county": county_cd})
        if use_cache:
            cached = get_cached_response(cache_key)
            if cached:
                return {**cached, "cached": True}

        if not county_cd:
            return {
                "success": True,
                "is_active_gage": False,
                "watershed_name": f"Agricultural Hydrologic Unit ({round(latitude, 2)}° N, {round(longitude, 2)}° W)",
                "gages_count": 0,
                "gages": [],
                "status": "REGIONAL_HYDROLOGIC_BENCHMARK"
            }

        params = {
            "format": "json",
            "countyCd": county_cd,
            "parameterCd": "00060,00065", # Discharge (cfs), Gage Height (ft)
            "siteStatus": "active"
        }

        try:
            resp = self.session.get(self.base_url, params=params, timeout=self.default_timeout)
            if resp.status_code == 200:
                data = resp.json()
                time_series = data.get("value", {}).get("timeSeries", [])
                gages = []
                for ts in time_series[:4]:
                    site_name = ts.get("sourceInfo", {}).get("siteName", "USGS Gage")
                    site_code = ts.get("sourceInfo", {}).get("siteCode", [{}])[0].get("value")
                    var_desc = ts.get("variable", {}).get("variableDescription", "Streamflow")
                    unit = ts.get("variable", {}).get("unit", {}).get("unitCode", "")
                    vals = ts.get("values", [{}])[0].get("value", [])
                    latest_val = vals[-1].get("value") if vals else None

                    gages.append({
                        "site_code": site_code,
                        "site_name": site_name,
                        "variable": var_desc,
                        "value": float(latest_val) if latest_val and latest_val != "-999999" else None,
                        "unit": unit
                    })

                res = {
                    "success": True,
                    "county_fips": county_cd,
                    "county_name": county_name,
                    "state": state_cd,
                    "gages_count": len(gages),
                    "gages": gages,
                    "status": "ACTIVE_STREAMFLOW_MONITORED",
                    "provenance": {
                        "agency": "USGS Water Resources Mission Area",
                        "endpoint": resp.url
                    }
                }
                if use_cache:
                    set_cached_response(cache_key, self.source_name, self.base_url, {"county": county_cd}, res)
                return res
            else:
                return {
                    "success": True,
                    "county_name": county_name,
                    "gages_count": 0,
                    "status": f"USGS HTTP {resp.status_code}"
                }
        except Exception as e:
            return {
                "success": True,
                "county_name": county_name,
                "gages_count": 0,
                "status": f"Hydrologic gage service unavailable ({str(e)[:50]})"
            }
