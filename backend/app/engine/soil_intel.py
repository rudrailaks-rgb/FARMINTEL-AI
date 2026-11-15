"""
FARMINTEL AI - Soil Intelligence Engine
Interprets USDA NRCS SSURGO edaphic profiles into actionable agricultural parameters:
- Available Water Capacity (AWC) rating & root-zone reservoir depth
- Textural suitability & tillage workability
- Soil organic matter (SOM) buffer & microbial activity capacity
- Soil reaction (pH) & nutrient bioavailability index
- Internal drainage, waterlogging hazard, and hydrologic runoff risk
"""

from typing import Dict, Any, List

class SoilIntelligenceEngine:
    @staticmethod
    def evaluate_soil_health(ssurgo_data: Dict[str, Any]) -> Dict[str, Any]:
        if not ssurgo_data.get("success"):
            return {
                "error": ssurgo_data.get("error", "Unable to evaluate soil health without valid SSURGO data")
            }

        topsoil = ssurgo_data.get("topsoil_properties", {})
        comp = ssurgo_data.get("dominant_component", {})
        profile = ssurgo_data.get("profile_metrics", {})

        ph = topsoil.get("ph_water", 6.5)
        om = topsoil.get("organic_matter_pct", 3.0)
        texture = topsoil.get("texture_class", "Loam")
        awc_total = profile.get("total_available_water_capacity_100cm_cm", 18.0)
        drainage = comp.get("drainage_class", "Well drained")
        hydgrp = comp.get("hydrologic_group", "B")

        # 1. Available Water Capacity Index (0 - 100)
        # Deep silt loam soils in Corn Belt often have AWC > 20 cm in 100cm profile
        if awc_total >= 22.0:
            awc_score = 95
            awc_rating = "Very High (Excellent Drought Buffer)"
        elif awc_total >= 18.0:
            awc_score = 85
            awc_rating = "High (Strong Moisture Retention)"
        elif awc_total >= 12.0:
            awc_score = 70
            awc_rating = "Moderate (Average Retention)"
        else:
            awc_score = 45
            awc_rating = "Low (Drought Sensitive / Coarse Matrix)"

        # 2. Organic Matter Health (0 - 100)
        # Corn belt prairie soils (Mollisols) historically had 4-7% OM; depleted soils < 2.5%
        if om >= 4.0:
            om_score = 95
            om_status = "Exceptional (High Native Mollisol Fertility)"
        elif om >= 3.0:
            om_score = 80
            om_status = "Good (Sufficient Nutrient Buffer)"
        elif om >= 2.0:
            om_score = 60
            om_status = "Moderate (Rebuilding Needed via Cover Crops/Residue)"
        else:
            om_score = 40
            om_status = "Depleted (High Degradation Risk; Priority for Legume/Cover)"

        # 3. pH Reaction & Nutrient Bioavailability (0 - 100)
        # Optimal for corn/soy/wheat: 6.2 to 7.3; alfalfa prefers 6.8 to 7.2
        if 6.2 <= ph <= 7.3:
            ph_score = 95
            ph_status = "Optimal Bioavailability"
        elif 5.8 <= ph < 6.2 or 7.3 < ph <= 7.8:
            ph_score = 75
            ph_status = "Slightly Constrained (Tolerable for Corn/Wheat; Marginal for Alfalfa)"
        elif ph < 5.8:
            ph_score = 50
            ph_status = "Acidic (Al tie-up; Lime amendment recommended)"
        else:
            ph_score = 55
            ph_status = "Alkaline / Calcareous (P and Fe tie-up risk)"

        # 4. Drainage & Waterlogging Vulnerability
        drainage_lower = drainage.lower()
        if "poorly" in drainage_lower or "somewhat poorly" in drainage_lower:
            drainage_risk = "High Waterlogging Hazard (Tile Drainage or Tolerant Crops Required)"
            trafficability = "Delayed spring field access during wet planting windows"
        elif "moderately well" in drainage_lower or "well" in drainage_lower:
            drainage_risk = "Low Waterlogging Hazard"
            trafficability = "Good field trafficability after precipitation events"
        else:
            drainage_risk = "Rapidly Drained / Droughty"
            trafficability = "Immediate field access; rapid moisture loss"

        # 5. Composite Soil Health Score (0 - 100)
        composite_score = round((awc_score * 0.35) + (om_score * 0.35) + (ph_score * 0.30), 1)

        soil_indicators = [
            {
                "indicator_id": "SOIL_AWC",
                "name": "Profile Available Water Capacity",
                "value": round(awc_total, 1),
                "units": "cm water / 100cm profile",
                "score": awc_score,
                "rating": awc_rating,
                "definition": "Volume of water held between field capacity and permanent wilting point."
            },
            {
                "indicator_id": "SOIL_OM",
                "name": "Soil Organic Matter",
                "value": round(om, 2),
                "units": "% (weight)",
                "score": om_score,
                "rating": om_status,
                "definition": "Decomposed plant/animal residue driving cation exchange capacity and soil aggregation."
            },
            {
                "indicator_id": "SOIL_PH",
                "name": "Topsoil Reaction (pH 1:1 H2O)",
                "value": round(ph, 2),
                "units": "pH units",
                "score": ph_score,
                "rating": ph_status,
                "definition": "Chemical acidity/alkalinity controlling macro- and micro-nutrient solubility."
            },
            {
                "indicator_id": "SOIL_DRAINAGE",
                "name": "Internal Drainage Classification",
                "value": drainage,
                "units": "Class",
                "score": 85 if "well" in drainage_lower else 55,
                "rating": drainage_risk,
                "definition": "Natural rate of soil moisture transmission through the profile under gravity."
            }
        ]

        return {
            "composite_soil_health_score": composite_score,
            "soil_health_tier": "PRIME AGRICULTURAL" if composite_score >= 80 else ("PRODUCTIVE WITH MANAGEMENT" if composite_score >= 65 else "MANAGEMENT INTENSIVE"),
            "mapunit_name": ssurgo_data.get("mapunit", {}).get("name"),
            "dominant_series": comp.get("name"),
            "texture": texture,
            "trafficability": trafficability,
            "indicators": soil_indicators,
            "limitations": ssurgo_data.get("agronomic_limitations", [])
        }
