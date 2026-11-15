"""
FARMINTEL AI - Climate & Water Intelligence Engine
Calculates agricultural meteorological indicators from NASA POWER daily observations:
- Growing Degree Days (GDD Base 50°F / 10°C)
- Heat Stress Index (Days Tmax >= 35°C / 95°F and Tmax >= 32°C / 90°F)
- Precipitation Dynamics (Rainfall total, daily extremes, dry spell runs, coefficient of variation)
- Hargreaves-Samani Reference Evapotranspiration (ET0)
- Climatic Water Balance (Precipitation minus ET0)
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime

class ClimateIntelligenceEngine:
    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Computes agricultural climate indicators from a cleaned daily DataFrame.
        """
        if df.empty or len(df) < 5:
            return {"error": "Insufficient observations to compute climate indicators"}

        # 1. Thermal Metrics
        mean_t = round(float(df["T2M"].mean()), 2)
        max_t = round(float(df["T2M_MAX"].max()), 2)
        min_t = round(float(df["T2M_MIN"].min()), 2)

        # 2. Growing Degree Days (GDD, Base 10°C / 50°F, Upper Cutoff 30°C / 86°F for Corn/Soybeans)
        # Formula: max(0, ((min(Tmax, 30) + max(Tmin, 10)) / 2) - 10)
        adj_tmax = df["T2M_MAX"].clip(upper=30.0)
        adj_tmin = df["T2M_MIN"].clip(lower=10.0)
        daily_gdd = ((adj_tmax + adj_tmin) / 2.0 - 10.0).clip(lower=0.0)
        total_gdd_c = round(float(daily_gdd.sum()), 1)
        # Convert to Fahrenheit GDD (commonly used in US Midwest agronomy): GDD_F = GDD_C * 1.8
        total_gdd_f = round(total_gdd_c * 1.8, 1)

        # 3. Heat Stress Indicators
        heat_stress_days_35c = int((df["T2M_MAX"] >= 35.0).sum()) # >= 95°F
        heat_stress_days_32c = int((df["T2M_MAX"] >= 32.2).sum()) # >= 90°F
        tropical_nights_20c = int((df["T2M_MIN"] >= 20.0).sum())  # High nighttime respiration stress

        # 4. Precipitation Indicators
        total_precip_mm = round(float(df["PRECTOTCORR"].sum()), 2)
        total_precip_in = round(total_precip_mm / 25.4, 2)
        mean_daily_precip = round(float(df["PRECTOTCORR"].mean()), 2)
        max_single_day_rain_mm = round(float(df["PRECTOTCORR"].max()), 2)
        rain_days_count = int((df["PRECTOTCORR"] >= 1.0).sum())
        dry_days_count = int((df["PRECTOTCORR"] < 1.0).sum())

        # Consecutive dry spell calculation (consecutive days with rain < 1.0 mm)
        dry_mask = df["PRECTOTCORR"] < 1.0
        dry_runs = (~dry_mask).cumsum()[dry_mask]
        max_consecutive_dry_days = int(dry_runs.value_counts().max()) if not dry_runs.empty else 0

        # Precipitation variability (Coefficient of Variation)
        precip_std = float(df["PRECTOTCORR"].std())
        precip_cv = round((precip_std / mean_daily_precip) if mean_daily_precip > 0 else 0.0, 2)

        # 5. Reference Evapotranspiration (ET0) via Hargreaves-Samani Method
        # ET0 = 0.0023 * Ra * (Tmean + 17.8) * sqrt(Tmax - Tmin)
        # where Ra is converted from MJ/m^2/day to equivalent mm of water evaporation (1 MJ/m^2/day ≈ 0.408 mm/day)
        temp_diff = (df["T2M_MAX"] - df["T2M_MIN"]).clip(lower=0.1)
        # Solar radiation in mm/day equivalent
        ra_mm_equivalent = df["ALLSKY_SFC_SW_DWN"] * 0.408
        daily_et0 = 0.0023 * ra_mm_equivalent * (df["T2M"] + 17.8) * np.sqrt(temp_diff)
        daily_et0 = daily_et0.clip(lower=0.0, upper=15.0) # physical bounds
        total_et0_mm = round(float(daily_et0.sum()), 2)
        total_et0_in = round(total_et0_mm / 25.4, 2)

        # Climatic Water Balance (P - ET0)
        water_balance_mm = round(total_precip_mm - total_et0_mm, 2)
        water_balance_status = "SURPLUS" if water_balance_mm >= 0 else "DEFICIT"

        # 6. Monthly Breakdown for Charts
        df_copy = df.copy()
        df_copy["month_year"] = df_copy["date"].dt.strftime("%Y-%m")
        monthly_grouped = df_copy.groupby("month_year").agg({
            "T2M": "mean",
            "T2M_MAX": "mean",
            "T2M_MIN": "mean",
            "PRECTOTCORR": "sum",
            "ALLSKY_SFC_SW_DWN": "mean"
        }).reset_index()

        monthly_chart_data = []
        for _, row in monthly_grouped.iterrows():
            monthly_chart_data.append({
                "month": row["month_year"],
                "avg_temp_c": round(row["T2M"], 1),
                "avg_temp_f": round(row["T2M"] * 9/5 + 32, 1),
                "max_temp_c": round(row["T2M_MAX"], 1),
                "min_temp_c": round(row["T2M_MIN"], 1),
                "rainfall_mm": round(row["PRECTOTCORR"], 1),
                "rainfall_in": round(row["PRECTOTCORR"] / 25.4, 2),
                "solar_radiation": round(row["ALLSKY_SFC_SW_DWN"], 1)
            })

        # Assemble standardized indicators list with required definitions, formulas, and provenance
        indicators_list = [
            {
                "indicator_id": "GDD_BASE50",
                "name": "Growing Degree Days (GDD Base 50°F / 10°C)",
                "category": "Thermal & Phenology",
                "value": total_gdd_f,
                "units": "GDD (°F-days)",
                "metric_value_c": total_gdd_c,
                "metric_units_c": "GDD (°C-days)",
                "formula": "sum(max(0, ((min(Tmax, 30°C) + max(Tmin, 10°C)) / 2) - 10°C)) * 1.8",
                "definition": "Accumulated thermal energy driving crop development from planting to physiological maturity.",
                "source": "NASA POWER Daily T2M_MAX & T2M_MIN",
                "risk_rating": "Optimal" if total_gdd_f >= 2400 else ("Moderate" if total_gdd_f >= 1800 else "Short-season Limited"),
                "limitations": "Standard base 50°F is calibrated for corn and soybeans; small grains utilize base 32°F / 0°C."
            },
            {
                "indicator_id": "HEAT_STRESS_DAYS",
                "name": "Extreme Heat Stress Episodes",
                "category": "Thermal Risk",
                "value": heat_stress_days_35c,
                "units": "Days (Tmax >= 35°C / 95°F)",
                "secondary_value": heat_stress_days_32c,
                "secondary_units": "Days (Tmax >= 32°C / 90°F)",
                "formula": "count(days where T2M_MAX >= 35.0°C)",
                "definition": "Frequency of acute thermal spikes that disrupt pollination, pollen viability, and kernel set.",
                "source": "NASA POWER Daily T2M_MAX",
                "risk_rating": "Low" if heat_stress_days_35c <= 3 else ("Moderate" if heat_stress_days_35c <= 10 else "High Heat Risk"),
                "limitations": "Microclimatic cooling from crop canopy transpiration can dampen ambient air temperature."
            },
            {
                "indicator_id": "TOTAL_PRECIPITATION",
                "name": "Cumulative Seasonal Precipitation",
                "category": "Water Availability",
                "value": total_precip_in,
                "units": "Inches",
                "metric_value": total_precip_mm,
                "metric_units": "mm",
                "formula": "sum(daily PRECTOTCORR)",
                "definition": "Total atmospheric moisture input over the observation window.",
                "source": "NASA POWER MERRA-2 Corrected Precipitation",
                "risk_rating": "Adequate" if total_precip_in >= 18.0 else ("Moderate Deficit" if total_precip_in >= 12.0 else "Drought Prone"),
                "limitations": "Satellite reanalysis averages over grid cell; does not account for local runoff efficiency."
            },
            {
                "indicator_id": "REFERENCE_ET0",
                "name": "Reference Evapotranspiration (Hargreaves ET0)",
                "category": "Atmospheric Water Demand",
                "value": total_et0_in,
                "units": "Inches",
                "metric_value": total_et0_mm,
                "metric_units": "mm",
                "formula": "Hargreaves-Samani: 0.0023 * Ra * (Tmean + 17.8) * sqrt(Tmax - Tmin)",
                "definition": "Potential water loss from an extensive standardized well-watered reference grass surface.",
                "source": "NASA POWER T2M, T2M_MAX, T2M_MIN, ALLSKY_SFC_SW_DWN",
                "risk_rating": "High Demand" if total_et0_in > 25.0 else ("Moderate" if total_et0_in >= 15.0 else "Low"),
                "limitations": "Empirical temperature-radiation method; can overestimate slightly in windy semi-arid conditions."
            },
            {
                "indicator_id": "CLIMATIC_WATER_BALANCE",
                "name": "Climatic Water Balance (P - ET0)",
                "category": "Water Balance",
                "value": round(water_balance_mm / 25.4, 2),
                "units": "Inches (P - ET0)",
                "metric_value": water_balance_mm,
                "metric_units": "mm",
                "formula": "Total Precipitation - Total Reference ET0",
                "definition": "Net atmospheric water surplus or deficit available to replenish soil water reserves.",
                "source": "NASA POWER Integrated Water Balance",
                "risk_rating": "Surplus" if water_balance_mm >= 0 else ("Moderate Deficit" if water_balance_mm >= -150 else "Severe Moisture Deficit"),
                "limitations": "Does not incorporate starting soil water profile reserves from antecedent seasons."
            },
            {
                "indicator_id": "MAX_DRY_SPELL",
                "name": "Maximum Consecutive Dry Spell",
                "category": "Intra-Seasonal Drought",
                "value": max_consecutive_dry_days,
                "units": "Consecutive Days (Precip < 1mm)",
                "formula": "max(consecutive days with daily PRECTOTCORR < 1.0mm)",
                "definition": "Longest duration without ecologically significant rainfall.",
                "source": "NASA POWER Daily Precipitation Time-Series",
                "risk_rating": "Low" if max_consecutive_dry_days <= 10 else ("Moderate" if max_consecutive_dry_days <= 18 else "Severe Dry Spell"),
                "limitations": "High available water capacity soils can buffer dry spells of 14-20 days without crop wilting."
            }
        ]

        return {
            "summary": {
                "mean_temperature_c": mean_t,
                "mean_temperature_f": round(mean_t * 9/5 + 32, 1),
                "max_temperature_c": max_t,
                "min_temperature_c": min_t,
                "total_gdd_f": total_gdd_f,
                "total_gdd_c": total_gdd_c,
                "total_precip_in": total_precip_in,
                "total_precip_mm": total_precip_mm,
                "total_et0_in": total_et0_in,
                "total_et0_mm": total_et0_mm,
                "water_balance_mm": water_balance_mm,
                "water_balance_in": round(water_balance_mm / 25.4, 2),
                "water_balance_status": water_balance_status,
                "heat_stress_days_35c": heat_stress_days_35c,
                "max_consecutive_dry_days": max_consecutive_dry_days,
                "rain_days_count": rain_days_count,
                "dry_days_count": dry_days_count
            },
            "indicators": indicators_list,
            "monthly_chart_data": monthly_chart_data
        }
