"""
FARMINTEL AI - Crop Knowledge Engine
Extensible agronomic database grounded in USDA ARS, Land-Grant Extension (Iowa State, Purdue, Illinois),
and peer-reviewed agronomy.
Covers Cereals, Oilseeds, Pulses, Fiber, Forage, Cover Crops, and Specialty crops.
"""

from typing import Dict, Any, List, Optional

class CropKnowledgeEngine:
    CROPS_DATABASE: Dict[str, Dict[str, Any]] = {
        "corn": {
            "id": "corn",
            "name": "Corn (Zea mays)",
            "common_name": "Field Corn",
            "category": "Cereals",
            "lifecycle": "Annual",
            "seasonality": "Warm Season (Summer Annual)",
            "relative_maturity_days": "95 - 115 days (Midwest Hybrid)",
            "gdd_requirement_f": 2400, # Base 50°F
            "thermal_thresholds_c": {"min": 10.0, "opt": 28.0, "max": 35.0},
            "water_requirement_in": 20.0, # 500 - 650 mm
            "water_requirement_mm": 550,
            "drought_tolerance": "Moderate (Vulnerable during 2-week silking/tasseling window)",
            "nitrogen_fixing": False,
            "nitrogen_credit_lb_ac": 0,
            "nitrogen_demand_lb_ac": "140 - 200 lb/acre (High demand)",
            "root_system": "Fibrous root system; effective extraction to 3-5 feet",
            "soil_preferences": {
                "ph_min": 6.0, "ph_opt_min": 6.2, "ph_opt_max": 7.2, "ph_max": 7.8,
                "preferred_textures": ["Loam", "Silt Loam", "Clay Loam"],
                "tolerated_drainage": ["Well drained", "Moderately well drained", "Tile-drained somewhat poorly"]
            },
            "rotation_benefits": "High residue biomass generation (OM preservation); excellent economic return.",
            "rotation_vulnerabilities": "Monoculture continuous corn intensifies Northern Corn Leaf Blight, Gray Leaf Spot, Corn Rootworm (Diabrotica spp.), and heavy synthetic N demand.",
            "compatible_preceding": ["soybeans", "alfalfa", "red_clover", "hairy_vetch", "field_peas"],
            "compatible_following": ["soybeans", "cereal_rye", "winter_wheat", "oats"],
            "pest_disease_notes": "Corn rootworm, European corn borer, Tar spot (Phyllachora maydis), Goss's wilt.",
            "economic_profile": "High volume, liquid commodity market; ethanol, livestock feed, and export.",
            "source_references": "Iowa State University Extension PM 1813; Purdue University Corn & Soybean Field Guide."
        },
        "soybeans": {
            "id": "soybeans",
            "name": "Soybeans (Glycine max)",
            "common_name": "Soybeans",
            "category": "Oilseeds / Legumes",
            "lifecycle": "Annual",
            "seasonality": "Warm Season (Summer Annual)",
            "relative_maturity_days": "100 - 125 days (Group II / III Midwest)",
            "gdd_requirement_f": 2200,
            "thermal_thresholds_c": {"min": 10.0, "opt": 27.0, "max": 34.0},
            "water_requirement_in": 18.0,
            "water_requirement_mm": 450,
            "drought_tolerance": "Moderate (Indeterminate types recover if rain arrives during pod fill R3-R5)",
            "nitrogen_fixing": True,
            "nitrogen_credit_lb_ac": 40, # Symbiotic fixation with Bradyrhizobium japonicum (30-50 lb N/ac carryover)
            "nitrogen_demand_lb_ac": "Low supplemental N needed if well nodulated",
            "root_system": "Taproot system with lateral branching up to 3-4 feet",
            "soil_preferences": {
                "ph_min": 6.0, "ph_opt_min": 6.3, "ph_opt_max": 7.0, "ph_max": 7.5,
                "preferred_textures": ["Loam", "Silt Loam", "Clay Loam", "Sandy Clay Loam"],
                "tolerated_drainage": ["Well drained", "Moderately well drained"]
            },
            "rotation_benefits": "Fixes atmospheric nitrogen; reduces corn rootworm pressure; lower residue simplifies following no-till pass.",
            "rotation_vulnerabilities": "Fragile residue leaves soil vulnerable to post-harvest erosion unless winter cover is seeded.",
            "compatible_preceding": ["corn", "winter_wheat", "grain_sorghum", "oats"],
            "compatible_following": ["corn", "winter_wheat", "cereal_rye"],
            "pest_disease_notes": "Soybean Cyst Nematode (Heterodera glycines), Sudden Death Syndrome (Fusarium virguliforme), White mold.",
            "economic_profile": "High value oilseed and protein meal; major international export commodity.",
            "source_references": "University of Illinois Extension Agronomy Handbook; USDA ARS Soybean Research."
        },
        "winter_wheat": {
            "id": "winter_wheat",
            "name": "Winter Wheat (Triticum aestivum)",
            "common_name": "Soft Red / Hard Red Winter Wheat",
            "category": "Cereals",
            "lifecycle": "Annual",
            "seasonality": "Cool Season (Overwinters; planted Sept-Oct, harvested June-July)",
            "relative_maturity_days": "240 - 280 days (including winter vernalization)",
            "gdd_requirement_f": 1800, # Base 32°F / 0°C calculation
            "thermal_thresholds_c": {"min": 4.0, "opt": 20.0, "max": 30.0},
            "water_requirement_in": 14.0,
            "water_requirement_mm": 350,
            "drought_tolerance": "High (Matures before July/August peak summer heat and drought)",
            "nitrogen_fixing": False,
            "nitrogen_credit_lb_ac": 0,
            "nitrogen_demand_lb_ac": "70 - 100 lb/acre (Spring top-dress)",
            "root_system": "Extensive fibrous root network stabilizing top 2 feet",
            "soil_preferences": {
                "ph_min": 5.8, "ph_opt_min": 6.0, "ph_opt_max": 7.2, "ph_max": 8.0,
                "preferred_textures": ["Silt Loam", "Loam", "Clay Loam"],
                "tolerated_drainage": ["Well drained", "Moderately well drained; intolerant of ponded standing water"]
            },
            "rotation_benefits": "Breaks warm-season weed and insect cycles; protects soil through winter; provides July double-crop window.",
            "rotation_vulnerabilities": "Requires timely planting after soybean harvest before freeze.",
            "compatible_preceding": ["soybeans", "field_peas", "corn"],
            "compatible_following": ["red_clover", "soybeans (double crop)", "corn", "alfalfa"],
            "pest_disease_notes": "Fusarium head blight (scab), Stripe rust, Septoria leaf blotch, Hessian fly.",
            "economic_profile": "Flour and cereal milling; straw provides valuable livestock bedding or mulch.",
            "source_references": "Ohio State University Extension Bulletin 814; Kansas State University Wheat Production Handbook."
        },
        "grain_sorghum": {
            "id": "grain_sorghum",
            "name": "Grain Sorghum / Milo (Sorghum bicolor)",
            "common_name": "Milo",
            "category": "Cereals",
            "lifecycle": "Annual",
            "seasonality": "Warm Season (Summer Annual)",
            "relative_maturity_days": "95 - 120 days",
            "gdd_requirement_f": 2200,
            "thermal_thresholds_c": {"min": 15.0, "opt": 30.0, "max": 38.0},
            "water_requirement_in": 14.0,
            "water_requirement_mm": 350,
            "drought_tolerance": "Exceptional (C4 photosynthetic efficiency with waxy leaf cuticle and dormancy during acute drought)",
            "nitrogen_fixing": False,
            "nitrogen_credit_lb_ac": 0,
            "nitrogen_demand_lb_ac": "80 - 120 lb/acre (30-40% less than corn)",
            "root_system": "Deep fibrous root system penetrating up to 5-6 feet with twice the root density of corn",
            "soil_preferences": {
                "ph_min": 5.5, "ph_opt_min": 6.0, "ph_opt_max": 7.5, "ph_max": 8.5,
                "preferred_textures": ["Loam", "Clay Loam", "Sandy Loam", "Clay"],
                "tolerated_drainage": ["Well drained", "Moderately well drained", "Tolerates heavier clay"]
            },
            "rotation_benefits": "Premier climate-resilient alternative to corn; high root biomass improves soil aggregation; reduces corn rootworm.",
            "rotation_vulnerabilities": "Slower early seedling vigor; requires warm soil at planting (>65°F).",
            "compatible_preceding": ["soybeans", "winter_wheat", "alfalfa"],
            "compatible_following": ["soybeans", "winter_wheat", "sunflower"],
            "pest_disease_notes": "Sugarcane aphid, Sorghum midge, Anthracnose, Head blight.",
            "economic_profile": "Livestock feed, ethanol feedstock, and growing gluten-free human food market.",
            "source_references": "Texas A&M AgriLife Sorghum Production Guide; USDA NRCS Sorghum Guidelines."
        },
        "cereal_rye": {
            "id": "cereal_rye",
            "name": "Cereal Rye (Secale cereale)",
            "common_name": "Winter Cereal Rye",
            "category": "Forage / Cover Crops",
            "lifecycle": "Annual",
            "seasonality": "Cool Season (Winter Cover Crop)",
            "relative_maturity_days": "Cover termination: 180 - 210 days; Grain: 270 days",
            "gdd_requirement_f": 1200,
            "thermal_thresholds_c": {"min": 2.0, "opt": 18.0, "max": 28.0},
            "water_requirement_in": 8.0,
            "water_requirement_mm": 200,
            "drought_tolerance": "Very High (Germinates in cool, dry autumn soils; active growth resume at 38°F)",
            "nitrogen_fixing": False,
            "nitrogen_credit_lb_ac": 0, # Scavenges 40 - 80 lb N/ac that would otherwise leach into tile lines
            "nitrogen_demand_lb_ac": "Minimal (Scavenger crop)",
            "root_system": "Massive dense root web in top 12 inches; excellent soil armor against spring runoff",
            "soil_preferences": {
                "ph_min": 5.0, "ph_opt_min": 5.8, "ph_opt_max": 7.0, "ph_max": 8.0,
                "preferred_textures": ["Sandy Loam", "Loam", "Silt Loam", "Clay Loam"],
                "tolerated_drainage": ["Well drained", "Somewhat poorly drained"]
            },
            "rotation_benefits": "Foremost cover crop in Corn Belt; suppresses waterhemp and Palmer amaranth via allelopathy; cuts nitrate leaching by 40-70%.",
            "rotation_vulnerabilities": "Must be terminated 10-14 days before corn planting to avoid nitrogen immobilization and seedling disease.",
            "compatible_preceding": ["corn", "soybeans", "silage"],
            "compatible_following": ["soybeans", "corn (with managed termination)"],
            "pest_disease_notes": "Can host true armyworm if termination is delayed.",
            "economic_profile": "Soil health investment; seed grain market or livestock forage grazing.",
            "source_references": "Midwest Cover Crops Council Field Guide; Iowa Learning Farms Cover Crop Trial Data."
        },
        "red_clover": {
            "id": "red_clover",
            "name": "Red Clover (Trifolium pratense)",
            "common_name": "Red Clover",
            "category": "Forage / Legume Cover",
            "lifecycle": "Biennial / Short-lived Perennial",
            "seasonality": "Cool Season Legume",
            "relative_maturity_days": "Frost-seeded in winter wheat; grows through summer/fall",
            "gdd_requirement_f": 1400,
            "thermal_thresholds_c": {"min": 7.0, "opt": 22.0, "max": 30.0},
            "water_requirement_in": 12.0,
            "water_requirement_mm": 300,
            "drought_tolerance": "Moderate (Taproot reaches 2-3 feet)",
            "nitrogen_fixing": True,
            "nitrogen_credit_lb_ac": 80, # Provides 70 - 110 lb N/ac credit to following corn crop
            "nitrogen_demand_lb_ac": "Zero (Inoculated with Rhizobium trifolii)",
            "root_system": "Deep branching taproot that aerates compacted subsoil",
            "soil_preferences": {
                "ph_min": 6.0, "ph_opt_min": 6.3, "ph_opt_max": 7.0, "ph_max": 7.5,
                "preferred_textures": ["Loam", "Silt Loam", "Clay Loam"],
                "tolerated_drainage": ["Moderately well drained", "Tolerates wetter soils better than alfalfa"]
            },
            "rotation_benefits": "Exceptional nitrogen generator for Corn-Soybean-Wheat rotations; high quality hay or plow-down green manure.",
            "rotation_vulnerabilities": "Requires small grain nurse crop or dedicated seeding window.",
            "compatible_preceding": ["winter_wheat", "oats", "barley"],
            "compatible_following": ["corn", "grain_sorghum"],
            "pest_disease_notes": "Sclerotinia crown rot, Clover root borer.",
            "economic_profile": "Reduces synthetic N fertilizer purchases by $40-$70/acre for the succeeding crop.",
            "source_references": "Michigan State University Extension Red Clover Agronomy; Penn State Agronomy Guide."
        },
        "alfalfa": {
            "id": "alfalfa",
            "name": "Alfalfa (Medicago sativa)",
            "common_name": "Alfalfa / Lucerne",
            "category": "Forage / Perennial Legume",
            "lifecycle": "Perennial (3 - 5 year stand)",
            "seasonality": "Cool / Warm Season Perennial",
            "relative_maturity_days": "Multi-cut (3-4 cuts per season in Midwest)",
            "gdd_requirement_f": 1600,
            "thermal_thresholds_c": {"min": 5.0, "opt": 25.0, "max": 33.0},
            "water_requirement_in": 25.0,
            "water_requirement_mm": 650,
            "drought_tolerance": "High once established (Taps deep moisture down to 10-15 feet)",
            "nitrogen_fixing": True,
            "nitrogen_credit_lb_ac": 120, # First-year corn N credit: 100-150 lb N/ac; second-year: 50 lb N/ac
            "nitrogen_demand_lb_ac": "Zero (Symbiotic Sinorhizobium meliloti fixation)",
            "root_system": "Massive deep taproot penetrating 8 to 20 feet; fractures dense plow-pans",
            "soil_preferences": {
                "ph_min": 6.5, "ph_opt_min": 6.8, "ph_opt_max": 7.4, "ph_max": 8.0,
                "preferred_textures": ["Deep Loam", "Silt Loam", "Well Drained Sandy Loam"],
                "tolerated_drainage": ["Well drained only; highly intolerant of wet feet / poor internal drainage"]
            },
            "rotation_benefits": "Premier soil builder; massive N credit; virtually eliminates annual weeds during stand years; halts soil erosion.",
            "rotation_vulnerabilities": "High lime requirement; sensitive to standing water and soil compaction; autotoxicity prevents direct reseeding.",
            "compatible_preceding": ["corn", "oats", "winter_wheat"],
            "compatible_following": ["corn", "grain_sorghum", "potatoes"],
            "pest_disease_notes": "Alfalfa weevil, Potato leafhopper, Phytophthora root rot, Aphanomyces.",
            "economic_profile": "Premium dairy-quality forage market; strong cash crop for livestock operations.",
            "source_references": "University of Wisconsin Extension Alfalfa Management Guide; USDA NRCS National Agronomy Manual."
        },
        "oats": {
            "id": "oats",
            "name": "Oats (Avena sativa)",
            "common_name": "Spring Oats",
            "category": "Cereals",
            "lifecycle": "Annual",
            "seasonality": "Cool Season (Early Spring seeded)",
            "relative_maturity_days": "75 - 90 days",
            "gdd_requirement_f": 1300,
            "thermal_thresholds_c": {"min": 4.0, "opt": 18.0, "max": 28.0},
            "water_requirement_in": 12.0,
            "water_requirement_mm": 300,
            "drought_tolerance": "Moderate (Avoids late summer heat by maturing in July)",
            "nitrogen_fixing": False,
            "nitrogen_credit_lb_ac": 0,
            "nitrogen_demand_lb_ac": "40 - 60 lb/acre",
            "root_system": "Fibrous root system",
            "soil_preferences": {
                "ph_min": 5.5, "ph_opt_min": 6.0, "ph_opt_max": 7.0, "ph_max": 7.5,
                "preferred_textures": ["Loam", "Silt Loam", "Sandy Loam"],
                "tolerated_drainage": ["Well drained", "Moderately well drained"]
            },
            "rotation_benefits": "Nurse crop for underseeded red clover or alfalfa; low input cost; early summer harvest creates diverse cover crop window.",
            "rotation_vulnerabilities": "Vulnerable to hot, dry weather during grain fill in late June.",
            "compatible_preceding": ["corn", "soybeans"],
            "compatible_following": ["red_clover", "alfalfa", "winter_wheat"],
            "pest_disease_notes": "Crown rust (Puccinia coronata), Barley yellow dwarf virus.",
            "economic_profile": "Food-grade milling oats, equine feed, and straw bales.",
            "source_references": "University of Minnesota Extension Small Grains Guide."
        },
        "hairy_vetch": {
            "id": "hairy_vetch",
            "name": "Hairy Vetch (Vicia villosa)",
            "common_name": "Hairy Vetch",
            "category": "Forage / Legume Cover",
            "lifecycle": "Winter Annual Legume",
            "seasonality": "Cool Season Winter Annual",
            "relative_maturity_days": "Planted Aug-Sept, terminates May",
            "gdd_requirement_f": 1300,
            "thermal_thresholds_c": {"min": 4.0, "opt": 20.0, "max": 28.0},
            "water_requirement_in": 10.0,
            "water_requirement_mm": 250,
            "drought_tolerance": "Moderate (Very winter-hardy compared to crimson clover)",
            "nitrogen_fixing": True,
            "nitrogen_credit_lb_ac": 100, # Can produce 90 - 150 lb N/acre when allowed to flower in May
            "nitrogen_demand_lb_ac": "Zero (Inoculated with Rhizobium leguminosarum)",
            "root_system": "Fibrous and taproot mixture; deep soil conditioning",
            "soil_preferences": {
                "ph_min": 5.5, "ph_opt_min": 6.0, "ph_opt_max": 7.0, "ph_max": 7.5,
                "preferred_textures": ["Sandy Loam", "Loam", "Silt Loam"],
                "tolerated_drainage": ["Well drained", "Intolerant of waterlogged ponding"]
            },
            "rotation_benefits": "Premier nitrogen-fixing winter cover preceding high-N demand crops like corn or sorghum; reduces synthetic fertilizer requirement.",
            "rotation_vulnerabilities": "Hard seed can volunteer in future small grain crops; vining habit requires roller-crimper or herbicide termination.",
            "compatible_preceding": ["corn_silage", "wheat", "early_soybean"],
            "compatible_following": ["corn", "grain_sorghum", "pumpkins"],
            "pest_disease_notes": "Can host root-knot nematodes in southern regions.",
            "economic_profile": "Significant input cost reduction through biological nitrogen fixation.",
            "source_references": "USDA Sustainable Agriculture Research & Education (SARE) Managing Cover Crops Profitably."
        },
        "tillage_radish": {
            "id": "tillage_radish",
            "name": "Tillage Radish / Daikon (Raphanus sativus)",
            "common_name": "Forage / Tillage Radish",
            "category": "Cover Crops / Brassicas",
            "lifecycle": "Fall Annual Cover Crop",
            "seasonality": "Late Summer / Fall Cover (Planted Aug, winterkills at 15-20°F)",
            "relative_maturity_days": "60 - 75 days to frost termination",
            "gdd_requirement_f": 900,
            "thermal_thresholds_c": {"min": 5.0, "opt": 18.0, "max": 26.0},
            "water_requirement_in": 8.0,
            "water_requirement_mm": 200,
            "drought_tolerance": "Moderate",
            "nitrogen_fixing": False,
            "nitrogen_credit_lb_ac": 0, # Scavenges up to 150 lb N/ac and releases it rapidly in spring
            "nitrogen_demand_lb_ac": "Responds strongly to residual N",
            "root_system": "Massive fleshy taproot ('biodrill') penetrating 1-3 feet and 1-3 inches thick",
            "soil_preferences": {
                "ph_min": 6.0, "ph_opt_min": 6.2, "ph_opt_max": 7.2, "ph_max": 7.8,
                "preferred_textures": ["Loam", "Silt Loam", "Clay Loam"],
                "tolerated_drainage": ["Well drained", "Moderately well drained"]
            },
            "rotation_benefits": "Alleviates soil compaction; leaves open root channels in spring that enhance rain infiltration and root growth; rapid winterkill eliminates spring termination hassle.",
            "rotation_vulnerabilities": "Distinctive decomposition odor in late winter; rapidly decomposes and leaves bare soil if not paired with a grass like cereal rye or oats.",
            "compatible_preceding": ["winter_wheat", "sweet_corn", "early_soybeans"],
            "compatible_following": ["corn", "soybeans"],
            "pest_disease_notes": "Flea beetles, Diamondback moth.",
            "economic_profile": "Biological tillage replacing expensive diesel subsoiling passes.",
            "source_references": "University of Maryland Extension Fact Sheet FS-824; NRCS Cover Crop Specifications."
        }
    }

    @classmethod
    def get_all_crops(cls) -> List[Dict[str, Any]]:
        return list(cls.CROPS_DATABASE.values())

    @classmethod
    def get_crop_by_id(cls, crop_id: str) -> Optional[Dict[str, Any]]:
        return cls.CROPS_DATABASE.get(crop_id.lower())

    @classmethod
    def filter_crops_by_suitability(
        cls,
        available_gdd: float,
        annual_precip_in: float,
        soil_ph: float,
        drainage_class: str
    ) -> List[Dict[str, Any]]:
        """
        Filters and ranks crops based on thermal, water, and soil constraints.
        """
        suitable = []
        for crop in cls.CROPS_DATABASE.values():
            score = 100
            reasons = []

            # GDD check
            req_gdd = crop.get("gdd_requirement_f", 2000)
            if available_gdd < req_gdd * 0.85:
                score -= 35
                reasons.append(f"Insufficient GDD (needs ~{req_gdd}, field has {available_gdd:.0f})")

            # Water check
            req_water = crop.get("water_requirement_in", 18.0)
            if annual_precip_in < req_water * 0.7:
                if crop.get("drought_tolerance") in ["High", "Very High", "Exceptional"]:
                    score -= 10
                    reasons.append("Low rainfall, but high drought resilience")
                else:
                    score -= 30
                    reasons.append(f"Water deficit risk (needs ~{req_water} in, rainfall {annual_precip_in:.1f} in)")

            # Soil pH check
            prefs = crop.get("soil_preferences", {})
            ph_min = prefs.get("ph_min", 5.5)
            ph_max = prefs.get("ph_max", 8.0)
            if soil_ph < ph_min or soil_ph > ph_max:
                score -= 25
                reasons.append(f"Soil pH {soil_ph:.1f} outside tolerance ({ph_min}-{ph_max})")

            # Drainage check
            drainage_lower = drainage_class.lower()
            if "poorly" in drainage_lower and crop["id"] in ["alfalfa", "grain_sorghum"]:
                score -= 30
                reasons.append(f"Intolerant of {drainage_class}")

            if score > 40:
                suitable.append({
                    "crop_id": crop["id"],
                    "crop_name": crop["name"],
                    "category": crop["category"],
                    "suitability_score": max(0, score),
                    "limiting_factors": reasons,
                    "crop_details": crop
                })

        suitable.sort(key=lambda x: x["suitability_score"], reverse=True)
        return suitable
