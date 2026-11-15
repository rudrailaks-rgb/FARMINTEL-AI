# Field Shift – Data Dictionary

This data dictionary defines all primary variables, physical units, observation frequencies, and provenance across the Field Shift data architecture.

---

### Table of Primary Variables

| Parameter Name | Dataset Source | Native Units | Transformation / Target Units | Physical Meaning | Valid Range | Missing Indicator |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PRECTOTCORR** | NASA POWER | mm/day | mm/day | Bias-corrected total precipitation | $[0, 500]$ | -999.0 |
| **T2M** | NASA POWER | °C | °C | Daily mean air temperature at 2 m | $[-10, 55]$ | -999.0 |
| **T2M_MAX** | NASA POWER | °C | °C | Daily maximum air temperature at 2 m | $[-5, 60]$ | -999.0 |
| **T2M_MIN** | NASA POWER | °C | °C | Daily minimum air temperature at 2 m | $[-10, 50]$ | -999.0 |
| **RH2M** | NASA POWER | % | % | Daily mean relative humidity at 2 m | $[0, 100]$ | -999.0 |
| **ALLSKY_SFC_SW_DWN** | NASA POWER | $MJ/m^2/day$ | $MJ/m^2/day$ | All-sky insolation incident on a horizontal surface | $[0, 40]$ | -999.0 |
| **Soil_Moisture_Surface** | SMAP SPL3SMP_E / SPL4SMGP | $cm^3/cm^3$ or $m^3/m^3$ | $m^3/m^3$ (volumetric) | Topsoil moisture (0-5 cm depth) | $[0.0, 0.65]$ | -9999.0 / NaN |
| **Soil_Moisture_Rootzone** | SMAP SPL4SMGP | $m^3/m^3$ | $m^3/m^3$ (volumetric) | Root-zone soil moisture (0-100 cm depth) | $[0.0, 0.65]$ | -9999.0 / NaN |
| **retrieval_qual_flag** | SMAP SPL3SMP_E | Bitmask/Enum | 0=Recommended, 1=Attempted, etc. | Surface soil moisture retrieval quality | 0 to 65535 | -1 |
| **NDVI** | MODIS MOD13Q1 | Scale factor 0.0001 (dimensionless) | Dimensionless $[-1.0, 1.0]$ | Normalized Difference Vegetation Index: $(NIR - Red) / (NIR + Red)$ | $[-0.2, 1.0]$ | -3000 |
| **EVI** | MODIS MOD13Q1 | Scale factor 0.0001 (dimensionless) | Dimensionless $[-1.0, 1.0]$ | Enhanced Vegetation Index: $2.5 \times (NIR - Red) / (NIR + 6 Red - 7.5 Blue + 1)$ | $[-0.2, 1.0]$ | -3000 |
| **pixel_reliability** | MODIS MOD13Q1 | Rank (0 to 3) | Categorical | 0=Good, 1=Marginal, 2=Snow/Ice, 3=Cloudy | $[0, 3]$ | 255 |
| **precipitationCal** | GPM IMERG Final | mm/hr | mm/day (accumulated) | Multi-satellite precipitation estimate with gauge calibration | $[0, 500]$ | -9999.9 |
| **phh2o** | ISRIC SoilGrids | $pH \times 10$ | pH units | Soil pH in 1:5 $H_2O$ suspension | $[3.0, 10.5]$ | -32768 |
| **soc** | ISRIC SoilGrids | $dg/kg$ ($g/kg \times 10$) | $g/kg$ or % organic carbon | Soil organic carbon stock / concentration | $[0, 100]$ | -32768 |
| **sand** | ISRIC SoilGrids | $g/kg$ ($10 \times \%$) | % ($g/kg \div 10$) | Sand fraction (0.05–2.0 mm particle size) | $[0, 100]$ | -32768 |
| **silt** | ISRIC SoilGrids | $g/kg$ ($10 \times \%$) | % ($g/kg \div 10$) | Silt fraction (0.002–0.05 mm particle size) | $[0, 100]$ | -32768 |
| **clay** | ISRIC SoilGrids | $g/kg$ ($10 \times \%$) | % ($g/kg \div 10$) | Clay fraction (<0.002 mm particle size) | $[0, 100]$ | -32768 |
| **bdod** | ISRIC SoilGrids | $cg/cm^3$ | $kg/dm^3$ ($g/cm^3$) | Bulk density of fine earth fraction | $[0.8, 2.0]$ | -32768 |
| **cec** | ISRIC SoilGrids | $mmol(c)/kg$ | $cmol(c)/kg$ | Cation Exchange Capacity at pH 7.0 | $[0, 100]$ | -32768 |
| **nitrogen** | ISRIC SoilGrids | $cg/kg$ | $g/kg$ | Total nitrogen content in fine earth fraction | $[0, 20]$ | -32768 |
| **Nino34_Index** | NOAA CPC | °C (anomaly) | °C | Sea surface temperature anomaly in Niño 3.4 region (5N-5S, 170W-120W) | $[-3.5, +3.5]$ | -99.99 |
| **DMI** | BOM Australia | °C (anomaly) | °C | Dipole Mode Index for Indian Ocean Dipole | $[-2.5, +2.5]$ | -99.99 |

---

### Geographic Reference Frame
- **Horizontal Coordinate Reference System (CRS):** EPSG:4326 (WGS84 ellipsoidal coordinates: Latitude, Longitude in decimal degrees).
- **Projected Coordinate Reference System for Local Buffers:** EPSG:32643 (WGS 84 / UTM zone 43N) where planar metric distances are required.
- **Vertical Datum:** EGM96 / WGS84 Ellipsoid.

