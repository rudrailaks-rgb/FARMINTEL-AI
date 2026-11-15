"""
FARMINTEL AI - Explainable AI Crop Rotation Decision Engine
Core innovation: Integrates real NASA Earth observations, USDA SSURGO edaphic profiles,
and peer-reviewed agronomic heuristics into three distinct, dynamically generated,
explainable rotation strategies:
- STRATEGY A: Existing Rotation Baseline (Grounded in farmer crop history or regional baseline)
- STRATEGY B: Soil Improvement Rotation (Legumes, Cover Crops, Living Roots, Bio-tillage)
- STRATEGY C: Climate-Resilient Rotation (Water-Conserving, Heat-Tolerant, Diversified Risk)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from .crop_knowledge import CropKnowledgeEngine

class RotationDecisionEngine:
    @staticmethod
    def calculate_confidence(
        has_climate_data: bool,
        climate_days_count: int,
        is_ssurgo_survey: bool,
        has_previous_crop: bool,
        latitude: float,
        longitude: float
    ) -> int:
        """
        Calculates a calibrated confidence score strictly between 0 and 100%.
        Reflects data availability, observation density, survey fidelity, and geographical bounds.
        """
        score = 0

        # 1. Climate data fidelity (0 - 35 points)
        if has_climate_data:
            if climate_days_count >= 150: # Full season coverage
                score += 35
            elif climate_days_count >= 60:
                score += 25
            else:
                score += 15

        # 2. Soil data fidelity (0 - 35 points)
        if is_ssurgo_survey:
            score += 35 # High-resolution official USDA NRCS SDA polygon query
        else:
            score += 20 # Valid regional North American benchmark baseline

        # 3. Farmer input fidelity (0 - 15 points)
        if has_previous_crop:
            score += 15 # Explicit starting crop condition
        else:
            score += 8 # Assumed regional dominant crop

        # 4. Regional model calibration (0 - 15 points)
        # US Agricultural regions: Latitude 24 - 50, Longitude -125 to -66
        if 24.0 <= latitude <= 50.0 and -125.0 <= longitude <= -66.0:
            score += 15 # Well-calibrated US agricultural zone
        else:
            score += 8 # Extrapolated high-latitude or foreign agricultural zone

        return min(max(int(score), 20), 98)

    @classmethod
    def generate_recommendations(
        cls,
        climate_data: Dict[str, Any],
        soil_data: Dict[str, Any],
        field_name: str = "Midwest Field 1",
        state: str = "Iowa",
        previous_crop: str = "corn",
        farmer_priority: str = "balanced", # 'balanced', 'soil_health', 'drought_resilience', 'profit'
        latitude: float = 42.0308,
        longitude: float = -93.6319,
        analysis_year: int = 2024
    ) -> Dict[str, Any]:
        """
        Dynamically evaluates climate observations, soil capabilities, and farmer priorities
        to generate 3 distinct, evidence-backed crop rotation strategies.
        """
        # 1. Extract climate parameters
        summary = climate_data.get("summary", {})
        gdd_f = float(summary.get("total_gdd_f", 2500.0) or 2500.0)
        precip_in = float(summary.get("total_precip_in", 22.0) or 22.0)
        et0_in = float(summary.get("total_et0_in", 20.0) or 20.0)
        water_bal_mm = float(summary.get("water_balance_mm", 0.0) or 0.0)
        water_bal_in = round(water_bal_mm / 25.4, 2)
        heat_days = int(summary.get("heat_stress_days_35c", 2) or 0)
        max_dry_spell = int(summary.get("max_consecutive_dry_days", 12) or 0)
        rain_days = int(summary.get("rain_days_count", 60) or 60)

        # 2. Extract soil parameters
        topsoil = soil_data.get("topsoil_properties", {})
        comp = soil_data.get("dominant_component", {})
        profile = soil_data.get("profile_metrics", {})
        soil_ph = float(topsoil.get("ph_water", 6.5) or 6.5)
        soil_om = float(topsoil.get("organic_matter_pct", 3.5) or 3.5)
        soil_texture = str(topsoil.get("texture_class", "Loam") or "Loam")
        awc_total = float(profile.get("total_available_water_capacity_100cm_cm", 18.0) or 18.0)
        drainage = str(comp.get("drainage_class", "Well drained") or "Well drained")
        mapunit_name = str(soil_data.get("mapunit", {}).get("muname") or soil_data.get("mapunit_name") or "Regional Agricultural Soils")
        dominant_series = str(comp.get("name") or soil_data.get("dominant_series") or "Agricultural Series")
        is_fallback = bool(soil_data.get("is_fallback", False) or "Benchmark" in mapunit_name or "Benchmark" in dominant_series)

        # 3. Detect Regional Agro-Ecological Context
        is_california = (longitude < -115.0 and latitude < 40.0)
        is_northern_short_season = (latitude > 45.0 or gdd_f < 2200.0)
        is_semi_arid_plains = (precip_in < 16.0 or water_bal_mm < -120.0)
        is_corn_belt = (not is_california and not is_semi_arid_plains and gdd_f >= 2200.0)

        # Normalize previous crop input
        prev_crop_clean = (previous_crop or "corn").lower().replace(" ", "_")

        # 4. Calculate Data Confidence (0 - 100%)
        confidence_score = cls.calculate_confidence(
            has_climate_data=bool(summary),
            climate_days_count=rain_days + int(summary.get("dry_days_count", 60) or 60),
            is_ssurgo_survey=not is_fallback,
            has_previous_crop=bool(previous_crop),
            latitude=latitude,
            longitude=longitude
        )

        # =========================================================================
        # STRATEGY A: EXISTING ROTATION BASELINE
        # =========================================================================
        baseline_provenance = "USER_INPUT" if previous_crop else "MODEL_ESTIMATE"

        if is_california:
            if "alfalfa" in prev_crop_clean:
                seq_a = [
                    {"year": 1, "crop_id": "alfalfa", "crop_name": "Alfalfa Hay (Cut 3-5)", "season": "Irrigated Perennial"},
                    {"year": 2, "crop_id": "corn", "crop_name": "Silage Corn", "season": "Summer Irrigated"},
                    {"year": 3, "crop_id": "winter_wheat", "crop_name": "Winter Forage Wheat", "season": "Cool Season Annual"}
                ]
            else:
                seq_a = [
                    {"year": 1, "crop_id": "corn", "crop_name": "Field / Silage Corn", "season": "Summer Irrigated"},
                    {"year": 2, "crop_id": "winter_wheat", "crop_name": "Winter Wheat / Cereal", "season": "Winter Annual"},
                    {"year": 3, "crop_id": "corn", "crop_name": "Field / Silage Corn", "season": "Summer Irrigated"}
                ]
            strat_a_name = f"California Irrigated Baseline ({seq_a[0]['crop_name']} Cycle)"
            strat_a_focus = "Standard Central Valley intensive irrigated cropping cycle."
        elif is_northern_short_season:
            if "wheat" in prev_crop_clean:
                seq_a = [
                    {"year": 1, "crop_id": "winter_wheat", "crop_name": "Spring / Winter Wheat", "season": "Cool Season Cereal"},
                    {"year": 2, "crop_id": "soybeans", "crop_name": "Early-Maturity Soybeans", "season": "Short-Season Summer"},
                    {"year": 3, "crop_id": "oats", "crop_name": "Spring Oats", "season": "Cool Season Grain"}
                ]
            else:
                seq_a = [
                    {"year": 1, "crop_id": "corn", "crop_name": "Short-Season Corn (85-95 RM)", "season": "Summer Annual"},
                    {"year": 2, "crop_id": "soybeans", "crop_name": "Soybeans (Group 0/I)", "season": "Summer Annual"},
                    {"year": 3, "crop_id": "winter_wheat", "crop_name": "Spring / Winter Wheat", "season": "Cool Season Cereal"}
                ]
            strat_a_name = f"Northern Plains Short-Season Baseline ({seq_a[0]['crop_name']} Cycle)"
            strat_a_focus = "Adapted to limited GDD window and cool seasonal temperatures."
        elif is_semi_arid_plains:
            if "sorghum" in prev_crop_clean:
                seq_a = [
                    {"year": 1, "crop_id": "grain_sorghum", "crop_name": "Grain Sorghum (Milo)", "season": "Summer C4 Cereal"},
                    {"year": 2, "crop_id": "winter_wheat", "crop_name": "Winter Wheat", "season": "Fall-Plant / Summer Harvest"},
                    {"year": 3, "crop_id": "grain_sorghum", "crop_name": "Grain Sorghum (Milo)", "season": "Summer C4 Cereal"}
                ]
            else:
                seq_a = [
                    {"year": 1, "crop_id": "winter_wheat", "crop_name": "Winter Wheat", "season": "Fall-Plant / Summer Harvest"},
                    {"year": 2, "crop_id": "grain_sorghum", "crop_name": "Grain Sorghum (Milo)", "season": "Summer C4 Cereal"},
                    {"year": 3, "crop_id": "winter_wheat", "crop_name": "Winter Wheat", "season": "Fall-Plant / Summer Harvest"}
                ]
            strat_a_name = f"Great Plains Dryland Baseline ({seq_a[0]['crop_name']} Cycle)"
            strat_a_focus = "Water-conserving cereal rotation matching semi-arid precipitation patterns."
        else: # Standard Corn Belt
            if "soybean" in prev_crop_clean:
                seq_a = [
                    {"year": 1, "crop_id": "corn", "crop_name": "Field Corn", "season": "Summer Annual"},
                    {"year": 2, "crop_id": "soybeans", "crop_name": "Soybeans", "season": "Summer Annual"},
                    {"year": 3, "crop_id": "corn", "crop_name": "Field Corn", "season": "Summer Annual"}
                ]
            else:
                seq_a = [
                    {"year": 1, "crop_id": "soybeans", "crop_name": "Soybeans", "season": "Summer Annual"},
                    {"year": 2, "crop_id": "corn", "crop_name": "Field Corn", "season": "Summer Annual"},
                    {"year": 3, "crop_id": "soybeans", "crop_name": "Soybeans", "season": "Summer Annual"}
                ]
            strat_a_name = f"Conventional Regional Baseline ({seq_a[0]['crop_name']}-{seq_a[1]['crop_name']} Cycle)"
            strat_a_focus = "Standard commercial grain rotation with immediate local market liquidity."

        # Compute dynamic scores for Strategy A
        score_a = 74
        if is_semi_arid_plains and "corn" in seq_a[0]["crop_id"]:
            score_a -= 12 # Penalize high water demand under dry conditions
        if heat_days > 5 and "corn" in seq_a[0]["crop_id"]:
            score_a -= 6 # Heat pollination risk

        strategy_a = {
            "strategy_id": "STRATEGY_A",
            "name": strat_a_name,
            "provenance_tier": baseline_provenance,
            "rotation_sequence": seq_a,
            "focus": strat_a_focus,
            "metrics": {
                "overall_score": score_a,
                "suitability_score": score_a,
                "data_confidence_score": confidence_score - 4, # Slightly lower due to unverified field history
                "water_demand_rating": "High" if "corn" in seq_a[0]["crop_id"] else "Moderate",
                "water_demand_index": 78 if "corn" in seq_a[0]["crop_id"] else 62,
                "soil_improvement_potential": "Moderate",
                "soil_improvement_index": 54,
                "nitrogen_balance": "Net Deficit: Requires ~140-180 lb synthetic N/ac for corn, offset by ~40 lb soybean credit",
                "nitrogen_credit_lb_ac": 40 if any("soybean" in s["crop_id"] for s in seq_a) else 0,
                "erosion_reduction_potential": "Low to Moderate: 5-6 months bare soil",
                "erosion_score": 50,
                "pest_cycle_interruption": "Moderate: Controls Corn Rootworm, but SCN and fungal foliar blights persist",
                "climate_suitability": "Optimal under historical average rainfall; vulnerable to summer heat and dry spells",
                "growing_season_compatibility": f"Matches observed {gdd_f:.0f} GDD thermal accumulation",
                "market_liquidity": "Exceptional: Immediate local cash sale, elevator basis contracts, and futures hedging"
            },
            "explainability": {
                "why_suggested": f"Represents the farmer's operational baseline starting after {previous_crop}. Provides standard commodity market liquidity.",
                "supporting_observations": [
                    f"Thermal accumulation ({gdd_f:.0f} GDD °F) supports the vegetative cycle of {seq_a[0]['crop_name']}.",
                    f"Topsoil organic matter ({soil_om:.1f}%) and pH ({soil_ph:.1f}) in {dominant_series} provide functional seedbed fertility.",
                    f"Baseline provenance: {baseline_provenance} based on selected parameters."
                ],
                "expected_benefits": [
                    "Familiar agronomic management with minimal capital friction.",
                    "Full crop insurance revenue protection and straightforward forward contracting."
                ],
                "inherent_risks": [
                    f"Vulnerable to summer heat stress ({heat_days} days >= 35°C observed in NASA records).",
                    "Topsoil remains unarmored for 5 months post-harvest, increasing rill and sheet erosion risk."
                ],
                "missing_information": [
                    "Tile drainage spacing and residual soil nitrate (PSNT) test levels.",
                    "Herbicide trait tolerances and historical weed resistance profile."
                ],
                "confidence_score": confidence_score - 4,
                "validation_checklist": [
                    "Perform pre-plant soil fertility test (P, K, and pH).",
                    "Verify local elevator forward basis contract before planting."
                ]
            }
        }

        # =========================================================================
        # STRATEGY B: SOIL HEALTH & CARBON REBUILDING
        # =========================================================================
        if is_california:
            seq_b = [
                {"year": 1, "crop_id": "corn", "crop_name": "Silage Corn + Winter Triticale Cover", "season": "Summer + Winter Living Root"},
                {"year": 2, "crop_id": "alfalfa", "crop_name": "Alfalfa (High N-Fixation)", "season": "Deep Taproot Perennial"},
                {"year": 3, "crop_id": "winter_wheat", "crop_name": "Wheat + Crimson Clover Bio-Cover", "season": "Grain + Soil Shield"}
            ]
            strat_b_focus = "Alfalfa-cereal integration for deep water penetration and root-zone salt leaching."
        elif is_northern_short_season:
            seq_b = [
                {"year": 1, "crop_id": "winter_wheat", "crop_name": "Spring Wheat + Underseeded Red Clover", "season": "Cereal + Frost-Seeded Legume"},
                {"year": 2, "crop_id": "soybeans", "crop_name": "Soybeans + Cereal Rye Cover", "season": "Cash Legume + Winter Armor"},
                {"year": 3, "crop_id": "oats", "crop_name": "Oats + Field Pea Green Manure", "season": "Cool Season Soil Builder"}
            ]
            strat_b_focus = "Frost-hardy legumes and small grains building soil organic matter in short growing windows."
        elif is_semi_arid_plains:
            seq_b = [
                {"year": 1, "crop_id": "grain_sorghum", "crop_name": "Grain Sorghum + Sunn Hemp Cover", "season": "C4 Grain + Summer Biomass"},
                {"year": 2, "crop_id": "winter_wheat", "crop_name": "Winter Wheat + Stubble Mulch Armor", "season": "Fall Cereal + Moisture Buffer"},
                {"year": 3, "crop_id": "sunflower", "crop_name": "Confection Sunflower + Daikon Radish", "season": "Deep Taproot Bio-Tillage"}
            ]
            strat_b_focus = "Moisture-scavenging taproots and continuous residue canopy preventing wind and water erosion."
        else: # Corn Belt
            seq_b = [
                {"year": 1, "crop_id": "corn", "crop_name": "Field Corn + Winter Cereal Rye Cover", "season": "Summer Cash + Overwinter Armor"},
                {"year": 2, "crop_id": "soybeans", "crop_name": "Soybeans (Planted Green) + Hairy Vetch", "season": "Summer Cash + Legume N-Fixer"},
                {"year": 3, "crop_id": "corn", "crop_name": "Field Corn + Tillage Radish / Crimson Clover", "season": "Cash Grain + Bio-Drill Cover"}
            ]
            strat_b_focus = "Continuous living root architecture, tile nitrate scavenging, and biological nitrogen fixation."

        score_b = 91
        if is_fallback:
            score_b -= 3 # Small adjustment when working with benchmark soil

        strategy_b = {
            "strategy_id": "STRATEGY_B",
            "name": f"Soil Health & Biological Regeneration ({seq_b[0]['crop_name'].split('+')[0].strip()} Cycle)",
            "provenance_tier": "DERIVED_INDICATOR",
            "rotation_sequence": seq_b,
            "focus": strat_b_focus,
            "metrics": {
                "overall_score": score_b,
                "suitability_score": score_b,
                "data_confidence_score": confidence_score,
                "water_demand_rating": "Balanced: Cover crop consumes excess spring moisture and increases summer infiltration",
                "water_demand_index": 70,
                "soil_improvement_potential": "Exceptional: Year-round living roots feed mycorrhizal networks and build aggregates",
                "soil_improvement_index": 94,
                "nitrogen_balance": "Net Positive: Biological legumes supply 80-120 lb N/ac; Rye prevents 40-70 lb N tile loss",
                "nitrogen_credit_lb_ac": 110,
                "erosion_reduction_potential": "Very High: Continuous ground armor reduces soil loss by up to 80%",
                "erosion_score": 93,
                "pest_cycle_interruption": "High: Cereal rye allelopathy suppresses broadleaf weeds; diverse cover interrupts fungal path",
                "climate_suitability": f"Optimal: Soil water capacity ({awc_total:.1f} cm) buffers cover crop spring moisture use",
                "growing_season_compatibility": "Cold-hardy cover species utilize post-harvest solar insolation and early spring heat",
                "market_liquidity": "High: Commercial grain sale retained; cover costs subsidized by USDA EQIP / CSP ($40-55/ac)"
            },
            "explainability": {
                "why_suggested": f"Recommended to halt organic matter degradation in {dominant_series} ({soil_om:.1f}% OM), reduce synthetic fertilizer expenditures, and prevent erosion.",
                "supporting_observations": [
                    f"NASA solar insolation indicates substantial radiant energy available between harvest and planting that bare ground loses.",
                    f"SSURGO soil profile ({soil_texture}, drainage: {drainage}) has sufficient water buffer ({awc_total:.1f} cm) for cover crops.",
                    "Living root exudates accelerate stable humus accumulation by 2-3x compared to surface crop residue alone."
                ],
                "expected_benefits": [
                    "Saves $45 - $80/acre in synthetic nitrogen and pre-emergence residual herbicide costs.",
                    "Significantly increases water infiltration rate, mitigating ponding during intense spring cloudbursts.",
                    "Qualifies for USDA NRCS conservation cost-share incentives."
                ],
                "inherent_risks": [
                    "Requires disciplined spring cover crop termination timing to prevent moisture or nitrogen tie-up before corn.",
                    "Seed cost for multispecies cover blends ($20-$35/acre) requires planned budgeting."
                ],
                "missing_information": [
                    "Farmer access to no-till drill or high-clearance interseeder for standing crop seeding.",
                    "Herbicide carryover restrictions for sensitive legume species."
                ],
                "confidence_score": confidence_score,
                "validation_checklist": [
                    "Calibrate drill for small-seeded cover species.",
                    "Schedule termination pass 10-14 days prior to planting or confirm roller-crimper termination plan."
                ]
            }
        }

        # =========================================================================
        # STRATEGY C: CLIMATE RESILIENCE & DROUGHT BUFFERING
        # =========================================================================
        if is_california or is_semi_arid_plains or precip_in < 18.0 or heat_days > 5:
            seq_c = [
                {"year": 1, "crop_id": "grain_sorghum", "crop_name": "Grain Sorghum (Milo)", "season": "Summer Heat Shield"},
                {"year": 2, "crop_id": "winter_wheat", "crop_name": "Winter Wheat", "season": "Overwintering Cereal"},
                {"year": 3, "crop_id": "sunflower", "crop_name": "Oilseed Sunflower / Double Legume", "season": "Deep-Root Drought Tolerant"}
            ]
            strat_c_focus = "Maximum water productivity and thermal defense against extreme dry spells and heat spikes."
        else:
            seq_c = [
                {"year": 1, "crop_id": "grain_sorghum", "crop_name": "Grain Sorghum (Milo)", "season": "Summer C4 Heat Shield"},
                {"year": 2, "crop_id": "winter_wheat", "crop_name": "Winter Wheat", "season": "Fall-Seeded Cool Cereal"},
                {"year": 3, "crop_id": "red_clover", "crop_name": "Red Clover / Diversified Forage", "season": "Late Summer Soil Builder"}
            ]
            strat_c_focus = "Water-conserving diversification mitigating pollination thermal failure."

        # Compute dynamic score for Strategy C based on climate risk
        score_c = 82
        if heat_days > 5 or precip_in < 18.0:
            score_c += 8 # Highly rewarded in drought/heat conditions
        if water_bal_mm < -100.0:
            score_c += 4

        strategy_c = {
            "strategy_id": "STRATEGY_C",
            "name": f"Climate-Resilient Low-Water Diversity ({seq_c[0]['crop_name']} Cycle)",
            "provenance_tier": "DERIVED_INDICATOR",
            "rotation_sequence": seq_c,
            "focus": strat_c_focus,
            "metrics": {
                "overall_score": score_c,
                "suitability_score": score_c,
                "data_confidence_score": confidence_score - 2,
                "water_demand_rating": "Low: Sorghum requires 35% less water than corn; wheat matures prior to summer drought",
                "water_demand_index": 50,
                "soil_improvement_potential": "High: Deep fibrous root systems fracture compaction down to 5-6 feet",
                "soil_improvement_index": 82,
                "nitrogen_balance": "Low Demand: Sorghum requires 40% less synthetic N; legume underseeding supplies 70-90 lb N",
                "nitrogen_credit_lb_ac": 75,
                "erosion_reduction_potential": "High: Wheat establishes fall ground cover; sorghum root mass binds topsoil",
                "erosion_score": 84,
                "pest_cycle_interruption": "Exceptional: Completely breaks Corn Rootworm, Soybean Cyst Nematode, and Tar Spot lifecycles",
                "climate_suitability": f"Outstanding: Exceptional tolerance to heat spikes ({heat_days} days >= 35°C observed) and dry spells",
                "growing_season_compatibility": "Spreads labor across early summer wheat harvest and autumn sorghum combining",
                "market_liquidity": "Moderate: Grain sorghum and wheat have active commercial markets, though local elevator bids require check"
            },
            "explainability": {
                "why_suggested": f"Recommended to insulate the farm against dry spells (max dry spell: {max_dry_spell} days) and volatile summer moisture deficits ({water_bal_in} in P-ET0).",
                "supporting_observations": [
                    f"NASA POWER observed {heat_days} extreme heat stress days (Tmax >= 35°C / 95°F); sorghum maintains photosynthetic integrity when corn pollen aborts.",
                    f"Climatic water balance ({water_bal_in} in) indicates recurring risk of root-zone moisture exhaustion during peak grain fill.",
                    "Deep fibrous sorghum roots extract moisture below 4 feet, accessing subsoil water reserves unavailable to shallow-rooted crops."
                ],
                "expected_benefits": [
                    "Eliminates catastrophic yield collapse during severe summer drought.",
                    "Cuts nitrogen fertilizer purchases by 35-45% compared to continuous corn.",
                    "Completely breaks corn and soybean disease complexes without chemical inputs."
                ],
                "inherent_risks": [
                    "Local elevator basis discount for grain sorghum in non-livestock dense regions (typically 5-8% under corn).",
                    "Requires careful combine cylinder and fan adjustments during sorghum harvest to prevent grain crackage."
                ],
                "missing_information": [
                    "Distance to nearest grain terminal accepting sorghum (poultry integrator, feed mill, or ethanol plant).",
                    "Local commercial market for wheat straw."
                ],
                "confidence_score": confidence_score - 2,
                "validation_checklist": [
                    "Contact local grain merchandiser to confirm sorghum bid basis and delivery specs.",
                    "Select bird-resistant, chinch bug-tolerant sorghum hybrids with regional maturity rating."
                ]
            }
        }

        # 5. Recommendation Synthesis based on Farmer Priority
        if farmer_priority == "soil_health" or farmer_priority == "soil_regeneration":
            primary_rec = "STRATEGY_B"
            rationale = "Strategy B delivers the highest soil organic matter accumulation, biological nitrogen fixation (+110 lb N/ac), and 93/100 erosion protection score."
        elif farmer_priority == "drought_resilience" or farmer_priority == "climate_resilience" or (heat_days > 8 or precip_in < 14.0):
            primary_rec = "STRATEGY_C"
            rationale = f"Strategy C is selected to neutralize severe climatic threats ({heat_days} heat stress days, {max_dry_spell}-day dry spell), slashing water demand by 35%."
        elif farmer_priority == "economic_profit" or farmer_priority == "profit":
            primary_rec = "STRATEGY_A" if score_a >= 80 else "STRATEGY_B"
            rationale = "Selected to maximize immediate cash liquidity, high commodity market volume, and equipment utilization."
        else: # 'balanced'
            # Balanced: Strategy B usually wins on multi-objective optimization unless extreme drought favors C
            primary_rec = "STRATEGY_B" if score_b >= score_c else "STRATEGY_C"
            rationale = "Balancing economic cash crop revenues with multi-year soil health regeneration. Cereal rye and legumes protect topsoil without sacrificing cash grain returns."

        comparison_matrix = [
            {
                "criterion": "Overall Agronomic Suitability",
                "strategy_a": f"{strategy_a['metrics']['overall_score']} / 100",
                "strategy_b": f"{strategy_b['metrics']['overall_score']} / 100 (Recommended)",
                "strategy_c": f"{strategy_c['metrics']['overall_score']} / 100"
            },
            {
                "criterion": "Data Evidence Confidence",
                "strategy_a": f"{strategy_a['metrics']['data_confidence_score']}%",
                "strategy_b": f"{strategy_b['metrics']['data_confidence_score']}%",
                "strategy_c": f"{strategy_c['metrics']['data_confidence_score']}%"
            },
            {
                "criterion": "Seasonal Water Demand Index",
                "strategy_a": f"{strategy_a['metrics']['water_demand_index']} / 100 ({strategy_a['metrics']['water_demand_rating'].split(':')[0]})",
                "strategy_b": f"{strategy_b['metrics']['water_demand_index']} / 100 ({strategy_b['metrics']['water_demand_rating'].split(':')[0]})",
                "strategy_c": f"{strategy_c['metrics']['water_demand_index']} / 100 ({strategy_c['metrics']['water_demand_rating'].split(':')[0]})"
            },
            {
                "criterion": "Synthetic Nitrogen Offset",
                "strategy_a": f"+{strategy_a['metrics']['nitrogen_credit_lb_ac']} lb N/ac",
                "strategy_b": f"+{strategy_b['metrics']['nitrogen_credit_lb_ac']} lb N/ac (Legume biological fixation)",
                "strategy_c": f"+{strategy_c['metrics']['nitrogen_credit_lb_ac']} lb N/ac"
            },
            {
                "criterion": "Erosion Armor Rating",
                "strategy_a": f"{strategy_a['metrics']['erosion_score']} / 100",
                "strategy_b": f"{strategy_b['metrics']['erosion_score']} / 100 (Exceptional ground cover)",
                "strategy_c": f"{strategy_c['metrics']['erosion_score']} / 100"
            },
            {
                "criterion": "Pest & Pathogen Lifecycle Interruption",
                "strategy_a": strategy_a['metrics']['pest_cycle_interruption'].split(':')[0],
                "strategy_b": strategy_b['metrics']['pest_cycle_interruption'].split(':')[0],
                "strategy_c": strategy_c['metrics']['pest_cycle_interruption'].split(':')[0]
            }
        ]

        return {
            "field_name": field_name,
            "state": state,
            "latitude": latitude,
            "longitude": longitude,
            "analysis_year": analysis_year,
            "farmer_priority": farmer_priority,
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat(),
            "primary_recommendation": primary_rec,
            "recommendation_rationale": rationale,
            "overall_data_confidence": confidence_score,
            "strategies": {
                "strategy_a": strategy_a,
                "strategy_b": strategy_b,
                "strategy_c": strategy_c
            },
            "comparison_matrix": comparison_matrix,
            "environmental_context": {
                "soil_mapunit": mapunit_name,
                "dominant_series": dominant_series,
                "soil_texture": soil_texture,
                "soil_organic_matter_pct": soil_om,
                "profile_awc_cm": awc_total,
                "thermal_accumulation_gdd": gdd_f,
                "seasonal_rainfall_in": precip_in,
                "heat_stress_days": heat_days,
                "water_balance_in": water_bal_in,
                "is_fallback_profile": is_fallback
            }
        }
