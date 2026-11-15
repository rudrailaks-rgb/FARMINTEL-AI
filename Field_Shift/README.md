# Field Shift: Uncertainty-Aware Agricultural Decision-Support System
## NASA Space Apps Challenge Research & Data Foundation

### Project Overview
**Field Shift** is an uncertainty-aware agricultural decision-support system designed to empower farmers and agricultural planners with explainable, scientifically defensible crop rotation recommendations. It seamlessly integrates:
- NASA Earth Observations (NASA POWER agroclimatology, SMAP soil moisture, MODIS vegetation health indices, GPM IMERG precipitation)
- Modeled and empirical soil profiles (ISRIC SoilGrids & Indian Soil Health Card program)
- Ground meteorological observations (India Meteorological Department - IMD)
- Regional agricultural statistics (Tamil Nadu Department of Economics & Statistics, Ministry of Agriculture & Farmers Welfare)
- Deep agronomic knowledge systems (Tamil Nadu Agricultural University - TNAU Agritech portal & ICAR)
- Teleconnections & macroclimate indices (ENSO Niño 3.4, Indian Ocean Dipole - IOD)

---

### Pilot Study Region: Athani, Erode District, Tamil Nadu
- **Country:** India (IN)
- **State:** Tamil Nadu (IN-TN, LGD Code: 33)
- **District:** Erode (LGD Code: 527, Census 2011 Code: 610)
- **Taluk / Sub-District:** Anthiyur (LGD Code: 5969, bifurcated from Bhavani Taluk)
- **Urban Local Body / Settlement:** Athani Selection Grade Town Panchayat (LGD ULB Code: 252536, Census 2011 Town Code: 803514)
- **PIN Code:** 638502
- **Verified Coordinates:**
  - Latitude: `11.523104° N`
  - Longitude: `77.514614° E`
  - OSM Centroid: `11.523530° N, 77.512429° E` (OSM Node: 1443165485, within 243 m along SH-82)
- **Spatial Scope:** Core Town Panchayat (~8.00 km²) and surrounding irrigated agrarian buffer zone (~78.5 km² - 100 km² Area of Interest) irrigated by the Lower Bhavani Project (LBP) canals and Bhavani River.
- **Primary Cropping Systems:** Sugarcane (*Saccharum officinarum*), Turmeric (*Curcuma longa*), Banana (*Musa acuminata*), Paddy (*Oryza sativa*), Maize (*Zea mays*), Coconut (*Cocos nucifera*), Groundnut (*Arachis hypogaea*), and Tapioca (*Manihot esculenta*).

---

### Project Directory Structure
```
Field_Shift/
│
├── data/
│   ├── raw/
│   │   ├── nasa_power/
│   │   ├── smap/
│   │   ├── modis/
│   │   ├── gpm/
│   │   ├── soilgrids/
│   │   ├── imd/
│   │   ├── crop_statistics/
│   │   ├── crop_characteristics/
│   │   └── enso_iod/
│   ├── processed/
│   ├── validated/
│   └── metadata/
│
├── boundaries/
│   ├── athani_study_area.geojson
│   └── boundary_metadata.json
│
├── scripts/
│   ├── download/
│   ├── inspect/
│   ├── preprocess/
│   └── validate/
│
├── reports/
│   ├── dataset_inventory.csv
│   ├── data_quality_report.md
│   └── acquisition_log.md
│
├── documentation/
│   ├── data_dictionary.md
│   ├── source_citations.md
│   └── limitations.md
│
└── README.md
```

---

### Research Period
- **Historical Analysis Window:** 2015-01-01 to 2025-12-31 (11 complete agricultural years)
- **Active Monitoring Window:** 2026 onwards

---

### Execution Protocol
The project strictly enforces:
1. **Provenance Preservation:** No overwriting of raw datasets; preservation of native file formats, units, and quality flags.
2. **Reproducibility:** All data acquisition, validation, and spatial extraction are automated via Python scripts located in `scripts/`.
3. **Traceability:** Every parameter and recommendation links back to peer-reviewed documentation or official institutional sources.
4. **Boundary Integrity:** All downloads are strictly spatially constrained to the verified Athani boundary.

