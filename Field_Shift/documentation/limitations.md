# Field Shift – Scientific Limitations & Uncertainty Considerations

This document articulates the inherent scientific assumptions, scale mismatches, uncertainty boundaries, and operational constraints across datasets used in the Field Shift system.

---

### 1. Spatial Resolution & Scale Mismatches
1. **Satellite vs. Farm-Scale Observations:**
   - **NASA POWER:** Employs a 0.5° × 0.5° (~55 km × 55 km) grid for atmospheric parameters and 0.1° (~10 km) for precipitation. While excellent for regional synoptic trends, microclimatic variations along the Bhavani riverbank or local topographical shade cannot be resolved.
   - **SMAP Soil Moisture:** Operates at 9 km (L3 Enhanced / L4) or 36 km (L3 Standard). A single 9 km SMAP pixel covers approximately 81 km²—spanning the entire Athani Town Panchayat plus adjacent villages. Individual field-level furrow or drip irrigation cannot be distinguished from background rainfed conditions; SMAP represents the integrated areal moisture state.
   - **MODIS Vegetation Indices (250 m):** A single 250 m pixel covers 6.25 hectares (approx. 15.4 acres). Smallholder field plots in Tamil Nadu often average 0.5 to 2.0 acres. Consequently, MODIS pixels frequently represent mixed cropping signatures (e.g., sugarcane intercropped with banana or fallow boundaries) rather than pure monoculture stands.
   - **GPM IMERG (0.1° / ~10 km):** Satellite precipitation estimates are derived from passive microwave and calibrated infrared radiometers, supplemented by GPCC gauge analysis. Convective localized pre-monsoon thunderstorms may show spatial displacement or smoothed intensities compared to in-situ raingauges.

2. **Gridded Model vs. Ground Truth:**
   - Neither NASA POWER, SMAP, GPM IMERG, nor SoilGrids represents direct in-situ field truth. They are physically-based or machine-learned gridded estimates.
   - Satellite estimates must never be reported or substituted as point ground station readings.

---

### 2. Edaphic & Soil Information (SoilGrids vs. Soil Health Cards)
1. **SoilGrids Limitations:**
   - SoilGrids is a global statistical machine-learning model (Random Forest / gradient boosting) driven by environmental covariates and point soil profiles.
   - Predictions carry quantifiable spatial uncertainty (represented by the 10th, 50th, and 90th percentiles). These uncertainty envelopes must be carried into crop decision models.
   - SoilGrids does not account for acute recent anthropogenic interventions (e.g., heavy chemical fertilizer application, gypsum amendments, or tank silt addition).
2. **Soil Health Cards (SHC):**
   - Laboratory measurements from Soil Health Cards provide authentic field-level chemical properties (Available N, P, K, micronutrients, EC, pH), but are spatially discrete and irregularly sampled across cropping cycles.

---

### 3. Agricultural Statistics Disaggregation
1. **Administrative Scale (District vs. Village):**
   - Government crop statistics from DES and DESAgri are compiled at the district level (Erode) and block level (Anthiyur).
   - District-level crop production averages do not imply uniform yield distribution across all farms in Athani, where canal irrigation access (Lower Bhavani Project) provides distinct yield resilience compared to rainfed uplands.

---

### 4. Macroclimate Teleconnections (ENSO / IOD)
1. **Non-Deterministic Indian Monsoon Teleconnections:**
   - While El Niño is historically correlated with suppressed Southwest Monsoon rainfall over central/north India, its impact on the **Northeast Monsoon (October–December)**—which is the primary agricultural rainfall season for Western Tamil Nadu and Erode—is frequently neutral to positive.
   - An El Niño or positive IOD event does not guarantee a specific drought or flood outcome in Athani. Teleconnection indices must be framed probabilistically rather than deterministically.

---

### 5. Access Control & NASA Earthdata Authentication
1. **Strict Authentication Compliance:**
   - Download workflows respect NASA Earthdata OAuth2 protocols. No authentication guards, token requirements, or scraping boundaries are bypassed.

