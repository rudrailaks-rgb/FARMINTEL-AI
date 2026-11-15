"""
FARMINTEL AI - Data Processing & Harmonization Engine
Handles data ingestion, validation, missing-value imputation, temporal alignment,
unit conversions, and multi-sensor spatial harmonization.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

class DataProcessingEngine:
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        if not (-90.0 <= lat <= 90.0):
            raise ValueError(f"Latitude must be between -90 and 90. Received {lat}")
        if not (-180.0 <= lon <= 180.0):
            raise ValueError(f"Longitude must be between -180 and 180. Received {lon}")
        return True

    @staticmethod
    def is_within_usa(lat: float, lon: float) -> bool:
        """Checks if coordinates fall roughly within continental USA, Alaska, or Hawaii bounds."""
        conus = (24.0 <= lat <= 50.0) and (-125.0 <= lon <= -66.0)
        alaska = (51.0 <= lat <= 72.0) and (-170.0 <= lon <= -129.0)
        hawaii = (18.5 <= lat <= 22.5) and (-161.0 <= lon <= -154.0)
        return conus or alaska or hawaii

    @staticmethod
    def process_climate_records(daily_records: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Converts daily weather records into a validated, cleaned, and sorted Pandas DataFrame.
        Fills isolated missing values via forward/backward fill and logs anomalies.
        """
        if not daily_records:
            return pd.DataFrame()

        df = pd.DataFrame(daily_records)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        numeric_cols = ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M", "ALLSKY_SFC_SW_DWN", "WS10M"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                # Forward-fill up to 2 consecutive missing days if any
                df[col] = df[col].ffill(limit=2).bfill(limit=2)

        return df

    @staticmethod
    def c_to_f(celsius: float) -> float:
        return round((celsius * 9.0 / 5.0) + 32.0, 2)

    @staticmethod
    def mm_to_inches(mm: float) -> float:
        return round(mm / 25.4, 2)

    @staticmethod
    def assess_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates completeness score and flags potential measurement irregularities."""
        if df.empty:
            return {"completeness_pct": 0.0, "status": "EMPTY", "flags": ["No data available"]}

        total_cells = df.size
        null_cells = df.isna().sum().sum()
        completeness = round(((total_cells - null_cells) / total_cells) * 100.0, 2)

        flags = []
        if (df["T2M_MAX"] < df["T2M_MIN"]).any():
            flags.append("Inconsistency detected: Tmax < Tmin on one or more dates")
        if (df["PRECTOTCORR"] < 0).any():
            flags.append("Negative precipitation detected and clamped to 0")
            df["PRECTOTCORR"] = df["PRECTOTCORR"].clip(lower=0)

        status = "EXCELLENT" if completeness >= 98.0 else ("GOOD" if completeness >= 90.0 else "DEGRADED")

        return {
            "completeness_pct": completeness,
            "status": status,
            "total_days": len(df),
            "date_range_start": df["date"].min().strftime("%Y-%m-%d"),
            "date_range_end": df["date"].max().strftime("%Y-%m-%d"),
            "flags": flags
        }
