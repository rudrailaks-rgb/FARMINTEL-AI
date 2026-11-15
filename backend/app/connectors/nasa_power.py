"""
FARMINTEL AI - NASA POWER Daily Agroclimatology Data Connector
Source: NASA Langley Research Center (LaRC)
API: https://power.larc.nasa.gov/api/temporal/daily/point
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from .base import BaseConnector, ConnectorResult
from ..config import settings

class NasaPowerConnector(BaseConnector):
    DEFAULT_PARAMETERS = [
        "T2M",               # Temperature at 2m (°C)
        "T2M_MAX",           # Maximum temperature (°C)
        "T2M_MIN",           # Minimum temperature (°C)
        "PRECTOTCORR",       # Corrected precipitation (mm/day)
        "RH2M",              # Relative humidity (%)
        "ALLSKY_SFC_SW_DWN", # All-sky solar insolation (MJ/m^2/day)
        "WS10M"              # Wind speed at 10m (m/s)
    ]

    PARAMETER_METADATA = {
        "T2M": {"name": "Mean Temperature", "units": "°C", "desc": "Daily mean temperature at 2 meters above ground"},
        "T2M_MAX": {"name": "Maximum Temperature", "units": "°C", "desc": "Daily maximum temperature at 2 meters"},
        "T2M_MIN": {"name": "Minimum Temperature", "units": "°C", "desc": "Daily minimum temperature at 2 meters"},
        "PRECTOTCORR": {"name": "Precipitation Corrected", "units": "mm/day", "desc": "MERRA-2 bias-corrected daily total precipitation"},
        "RH2M": {"name": "Relative Humidity", "units": "%", "desc": "Daily mean relative humidity at 2 meters"},
        "ALLSKY_SFC_SW_DWN": {"name": "Solar Radiation", "units": "MJ/m²/day", "desc": "CERES all-sky surface downward shortwave irradiance"},
        "WS10M": {"name": "Wind Speed", "units": "m/s", "desc": "Daily mean wind speed at 10 meters"}
    }

    def __init__(self):
        super().__init__(
            source_name="NASA_POWER",
            base_url=settings.NASA_POWER_BASE_URL,
            default_timeout=45
        )

    def fetch_daily_agroclimatology(
        self,
        latitude: float,
        longitude: float,
        start_date: str, # Format: YYYYMMDD
        end_date: str,   # Format: YYYYMMDD
        parameters: Optional[List[str]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Fetches daily agroclimatology data from NASA POWER for a given point and time window.
        """
        # Validate coordinates
        if not (-90.0 <= latitude <= 90.0):
            raise ValueError(f"Latitude must be between -90 and 90. Got {latitude}")
        if not (-180.0 <= longitude <= 180.0):
            raise ValueError(f"Longitude must be between -180 and 180. Got {longitude}")

        params_list = parameters or self.DEFAULT_PARAMETERS
        params_str = ",".join(params_list)

        query_params = {
            "parameters": params_str,
            "community": "AG", # Agroclimatology
            "longitude": f"{longitude:.5f}",
            "latitude": f"{latitude:.5f}",
            "start": start_date,
            "end": end_date,
            "format": "JSON"
        }

        result = self.get(params=query_params, use_cache=use_cache)
        if not result.success:
            return {
                "success": False,
                "error": result.error,
                "status_code": result.status_code,
                "latency_ms": result.latency_ms,
                "source": self.source_name
            }

        # Process and validate payload
        raw_data = result.data
        parsed_records, summary_stats = self._parse_and_validate(raw_data, params_list)

        elevation = raw_data.get("geometry", {}).get("coordinates", [0, 0, 0])[2]

        return {
            "success": True,
            "cached": result.cached,
            "latency_ms": result.latency_ms,
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "elevation_m": elevation
            },
            "date_range": {
                "start": start_date,
                "end": end_date,
                "days_count": len(parsed_records)
            },
            "parameters_metadata": self.PARAMETER_METADATA,
            "summary_statistics": summary_stats,
            "daily_records": parsed_records,
            "provenance": {
                "source_agency": "NASA Langley Research Center (LaRC)",
                "mission_model": "MERRA-2 Reanalysis & CERES Satellite Observations",
                "community": "Agroclimatology (AG)",
                "official_url": "https://power.larc.nasa.gov/"
            }
        }

    def _parse_and_validate(self, raw_json: Dict[str, Any], parameters: List[str]):
        properties = raw_json.get("properties", {})
        param_dict = properties.get("parameter", {})

        # Collect dates
        dates = sorted(list(next(iter(param_dict.values())).keys())) if param_dict else []
        records = []
        df_rows = []

        for d in dates:
            formatted_date = f"{d[:4]}-{d[4:6]}-{d[6:]}"
            record = {"date": formatted_date, "raw_date": d}
            row = {"date": formatted_date}

            for p in parameters:
                val = param_dict.get(p, {}).get(d)
                # Check for NASA POWER missing value indicators (-999 or -999.0)
                if val is None or val <= -990.0:
                    record[p] = None
                    row[p] = None
                else:
                    record[p] = round(float(val), 2)
                    row[p] = float(val)

            records.append(record)
            df_rows.append(row)

        df = pd.DataFrame(df_rows)
        summary = {}

        for p in parameters:
            if p in df.columns and not df[p].dropna().empty:
                valid_col = df[p].dropna()
                summary[p] = {
                    "count": int(len(valid_col)),
                    "missing": int(df[p].isna().sum()),
                    "mean": round(float(valid_col.mean()), 2),
                    "min": round(float(valid_col.min()), 2),
                    "max": round(float(valid_col.max()), 2),
                    "std": round(float(valid_col.std()), 2),
                    "sum": round(float(valid_col.sum()), 2) if "PREC" in p or "SW_DWN" in p else None
                }

        return records, summary
