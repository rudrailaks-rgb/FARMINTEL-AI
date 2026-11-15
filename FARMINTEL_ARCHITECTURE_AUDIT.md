# FARMINTEL AI — MASTER ARCHITECTURE & FULL SYSTEM AUDIT (PHASE 0)
**NASA Space Apps Challenge 2026: Field Shift — Adapting Farms with NASA Data**
**Date of Audit:** 2026-11-15T02:58:00+05:30 (UTC: 2026-11-14T21:28:00Z)
**Auditor / Engineering Role:** Senior Geospatial Architect, Full-Stack Engineer, Agricultural Data Scientist, QA Lead

---

## EXECUTIVE SUMMARY & FORENSIC INCIDENT ANALYSIS

This forensic audit investigates the critical defects identified in the running application:
1. **Invalid Longitude (`975.04789`) Allowed into System:** Longitude is physically constrained to $[-180.0, +180.0]$. The value `975.04789` is a typographical distortion of `-97.50478` (central Kansas/Great Plains) that was accepted by unvalidated frontend inputs and submitted to the API.
2. **Geospatial Desynchronization (Colorado Map vs. "Story County, Iowa" Label):** `fieldName` and county/state were stored as static disconnected strings in frontend state (`'Story County Iowa Pilot Field'`). When the user panned or clicked to Colorado/Kansas coordinates (`38.35454, ...`), the map pin updated, but the header and field card retained "Story County, Iowa" because the application completely lacks an automated reverse geocoding service.
3. **`[object Object]` Red Error Banner:** When the backend rejected invalid coordinates with a standard FastAPI/Pydantic 422 or 400 validation response (`{"detail": [{"loc": ["body", "longitude"], "msg": "..."}]}`), the frontend `api.ts` client threw `new Error(err.detail)`. In JavaScript, passing an array/object to `new Error()` produces the string `"[object Object]"`, which was rendered verbatim in the error banner.
4. **Hardcoded Decision Logic & Non-Responsive Rotation Objectives:** The optimizer possessed Pareto multi-objective math in `rotation_optimizer.py`, but the frontend `FieldControls.tsx` only updated a detached local variable `farmerPriority` without triggering re-optimization or re-ranking. Furthermore, the Rotations view (`RotationComparison.tsx`) lacked an in-situ objective selector, forcing Strategy B to remain permanently highlighted.
5. **Stale Data Retention on Field Change:** Modifying coordinates did not invalidate existing analysis data, allowing previous field results (e.g., Ames, IA Mollisol soil, rainfall, Landsat NDVI) to remain visible while viewing a different field.

---

## 1. COMPONENT-BY-COMPONENT ARCHITECTURAL AUDIT

| Feature / Component | Existing File Location | Actual Backend Endpoint | Actual Data Source | Works? | Hardcoded Values Present? | Root Cause of Failure | Required Correction |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **Coordinate Validation & Bounds Check** | `FieldControls.tsx`, `MapPicker.tsx`, `processing.py`, `field_state.py` | `POST /api/field/analyze` | User input / Map clicks | **NO** | No | Frontend inputs lack `min`, `max`, and immediate boundary validation (`-90` to `+90`, `-180` to `+180`). Backend `ValueError` was unhandled, producing raw 500/422 responses. | Add client-side validation, clamp/reject on input, add Pydantic custom validators, and return clean HTTP 400 with user-readable message. |
| **Reverse Geocoding & County Detection** | `field_state.py:92-104` | None (Hardcoded bounding box check) | None | **NO** | **YES** (`if (40 <= lat <= 43.5) state = "Iowa"`) | No geocoding service existed. Hardcoded bounding boxes only recognized Ames, IA, Fresno, CA, and Hall County, NE. All other US coordinates returned `None`. | Build `GeocodingService` in backend (using OpenStreetMap Nominatim / FCC Census / USGS GNIS) and call reverse geocoding on every coordinate change. |
| **Authoritative Field State** | `App.tsx:276-285`, `Header.tsx`, `FieldControls.tsx` | None (Scattered state in `App.tsx`) | Local React state | **PARTIAL** | **YES** (`fieldName` initialized to Story County) | Field state is scattered across 8 separate `useState` variables in `App.tsx`. Header displays `fieldName` while map displays new coordinates. | Create unified `FieldStateContext` / `useField` hook managing `field_id`, `coordinates`, `county`, `state`, `country`, and `analysis_year` synchronously. |
| **Error Handling & Error Banner** | `api.ts:53-55`, `App.tsx:434-444` | All endpoints | `res.json()` | **NO** | No | `api.ts` passes `err.detail` directly to `new Error()`. When `err.detail` is a Pydantic validation array, JS renders `[object Object]`. | Format API errors safely: extract `loc` and `msg` from arrays, serialize objects to string, and display clean messages. |
| **Geospatial Map Engine** | `MapPicker.tsx` | None (Client-side Leaflet) | OpenStreetMap & Esri World Imagery | **PARTIAL** | Yes (Longitude labeled as "°E") | Missing address/county search bar, no GeoJSON field boundary polygon drawing, label says "°E" for Western hemisphere. | Add search bar (Nominatim/USGS geocoding), add boundary drawing tool, fix hemisphere display ("°W"). |
| **Data Availability Service** | `official_registry.py` | `GET /api/datasets/registry` | Official Space Apps catalog | **PARTIAL** | No | Registry lists 28 datasets, but there is no runtime dynamic availability checker reporting coverage for the exact requested coordinates and date window. | Implement `DataAvailabilityService` returning `AVAILABLE`, `PARTIALLY_AVAILABLE`, `METADATA_ONLY`, `AUTH_REQUIRED`, `NO_COVERAGE`. |
| **NASA POWER Climate Intelligence** | `nasa_power.py`, `climate_intel.py`, `ClimateCharts.tsx` | `POST /api/field/analyze`, `GET /api/climate/*` | NASA POWER API (MERRA-2) | **YES** | No | Works well for valid CONUS points, but fails completely if coordinates are invalid. | Add coordinate guard before network call; show honest "Unavailable" state if NASA POWER is unreachable. |
| **USDA SSURGO Soil Intelligence** | `usda_ssurgo.py`, `soil_intel.py`, `SoilProfileCard.tsx` | `POST /api/field/analyze`, `GET /api/soil/*` | USDA NRCS SDA SQL API | **YES** | No | Works for CONUS; falls back cleanly outside CONUS, but map unit is not dynamically queried when panning before analysis. | Keep live SDA query; expose component and horizon details; link soil properties directly to crop constraints. |
| **ECMWF ERA5 Soil Moisture & Temp** | `era5_connector.py`, `ClimateCharts.tsx` | `POST /api/field/analyze` | Open-Meteo ERA5 0.25° Reanalysis | **YES** | No | Working live, 4 layers retrieved ($0-255\text{ cm}$). | Expose daily volumetric time-series alongside NASA POWER charts. |
| **USGS NWIS Hydrology** | `usgs_water_connector.py`, `NasaDataExplorer.tsx` | `POST /api/field/analyze` | USGS Waterservices REST | **YES** | No | Working live, queries nearby stations. | Explicitly label as "Watershed Hydrologic Context", not farm canal delivery. |
| **Landsat 8/9 Level-2 Raster Pipeline** | `landsat_raster_connector.py`, `NasaDataExplorer.tsx` | `POST /api/field/analyze` | Planetary Computer STAC & Azure COGs | **YES** | No | Working live; computes B4/B5 NDVI and 3x3 matrix. | Support multi-temporal seasonal acquisition scenes (Spring, Summer, Fall) when available. |
| **Crop Suitability Engine** | `crop_suitability_model.py`, `CropSuitabilityLab.tsx` | `POST /api/field/analyze`, `GET /api/crops` | ML Random Forest & Agronomic Envelopes | **PARTIAL** | **YES** (Synthetic envelopes) | Evaluates 10 crops, but target labels are synthetic-only. Suitability percentages are derived from envelope scores, not verified field yields. | Distinguish model score from data completeness; provide transparent supporting and limiting factors for each crop. |
| **Rotation Decision Engine & Optimizer** | `rotation_optimizer.py`, `RotationComparison.tsx` | `POST /api/field/analyze`, `POST /api/rotation/optimize` | Multi-objective Pareto algorithm | **PARTIAL** | **YES** (Strategy cards were static templates) | `RotationComparison.tsx` had no objective switcher. Clicking priorities in `FieldControls` did not re-rank strategies or re-run optimization. | Connect Strategic Priorities (Balanced, Max Profit, Soil Health, Resilience) directly to real-time Pareto weight calculation and dynamic plan recalculation. |
| **USDA NASS QuickStats** | `nass.py` (stubbed in official_registry) | None | USDA NASS API | **NO** | No | Requires API key; currently stubbed. | Implement real connector; if API key missing, return `AUTH_REQUIRED` with clear instructions, never mock yield. |
| **USDA AMS Market Prices** | `market_news.py` (stubbed) | None | USDA AMS Portal | **NO** | No | Stubbed; commodity price data not wired. | Return `AUTH_REQUIRED` / `UNAVAILABLE` rather than fabricating crop commodity prices. |
| **Database Persistence** | `database.py` (`farmintel.db`) | SQLite | Local SQLite3 DB | **YES** | No | Working live (`field_analyses` and `satellite_observations` tables persist all runs). | Add indexes on `latitude`, `longitude`, `field_id`, and `created_at` for faster geospatial lookup. |
| **Stale Data Invalidation** | `App.tsx` | None | Client-side state | **NO** | No | Changing coordinates kept old `analysisData` in memory until new analysis succeeded. | On coordinate change, immediately mark analysis data as dirty/stale or reset to unloaded state with explicit banner. |

---

## 2. DETAILED FORENSIC ROOT CAUSE ANALYSIS

### Root Cause 1: Coordinate Typo & Validation Gap (Longitude `975.04789`)
- **Frontend Source:** `frontend/src/components/FieldControls.tsx:125-134`:
  ```tsx
  <label className="block text-xs font-semibold text-slate-300 mb-1">
    Longitude (°E)
  </label>
  <input
    type="number"
    step="0.0001"
    value={longitude}
    onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
  />
  ```
  The input had no HTML5 `min="-180"` or `max="180"`, and no `onChange` bounds clamping.
- **Backend Source:** `backend/app/models/schemas.py`:
  ```python
  class FieldAnalysisRequest(BaseModel):
      latitude: float
      longitude: float
  ```
  `FieldAnalysisRequest` lacked Pydantic `Field(..., ge=-90.0, le=90.0)` and `Field(..., ge=-180.0, le=180.0)`.
- **Result:** `975.04789` was submitted directly to the server, crashing downstream services.

### Root Cause 2: `[object Object]` Error Banner
- **Frontend Source:** `frontend/src/api.ts:52-56`:
  ```typescript
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Field analysis failed');
  }
  ```
  FastAPI returns 422 Unprocessable Entity in the format:
  ```json
  {"detail": [{"loc": ["body", "longitude"], "msg": "Input should be less than or equal to 180", "type": "less_than_equal"}]}
  ```
  Calling `new Error(err.detail)` stringified the array of objects into `"[object Object]"`.
- **Display Source:** `frontend/src/App.tsx:439`:
  ```tsx
  <span>{error}</span>
  ```

### Root Cause 3: Desynchronization Between Map (Colorado) and Label ("Story County, Iowa")
- **Frontend Source:** `App.tsx:276`:
  ```tsx
  const [fieldName, setFieldName] = useState<string>('Story County Iowa Pilot Field');
  ```
  `fieldName` was never updated when `latitude` and `longitude` changed!
- **Backend Source:** `field_state.py:92-104` only inferred "Iowa", "California", or "Nebraska" via crude hardcoded boxes. Any point in Colorado ($38.35^\circ\text{ N}, -104.5^\circ\text{ W}$) returned `state: None`, `county: None`.
- **Result:** The map pin moved to Colorado, but `Header.tsx` kept rendering the static `fieldName` ("Story County Iowa Pilot Field").

### Root Cause 4: Optimizer Inaction on Objective Switch
- In `FieldControls.tsx`, priority buttons called `setFarmerPriority(p.id)`, but did not re-run analysis or re-rank plans.
- In `RotationComparison.tsx`, the Pareto weights had sliders, but the initial strategy selection was anchored to `decision.primary_recommendation` without dynamic recalculation when the user toggled objectives directly on the Rotations page.

---

## 3. ARCHITECTURAL REPAIR BLUEPRINT (PHASES 1 TO 15)

```
┌────────────────────────────────────────────────────────────────────────┐
│               PHASE 1: UNIFIED SELECTED-FIELD CONTEXT                  │
│   (Synchronous validation, reverse geocoding, dirty-state clearing)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               PHASE 2: ENHANCED MAP ENGINE WITH GEOCODER               │
│    (Leaflet, OpenStreetMap, county search, boundary drawing support)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│           PHASE 3: DATA AVAILABILITY & ORCHESTRATION SERVICE           │
│   (Dynamic per-coordinate coverage, source latency, fallback status)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│ Climate Engine  │        │   Soil Engine   │        │ Satellite Engine│
│   NASA POWER    │        │  USDA SSURGO    │        │  Landsat 8/9 C2 │
│   ECMWF ERA5    │        │  SDA Spatial    │        │  Multi-Temporal │
└────────┬────────┘        └────────┬────────┘        └────────┬────────┘
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 PHASE 7 & 8: DYNAMIC ROTATION OPTIMIZER                │
│    (Real multi-objective Pareto ranking: Balanced, Profit, Soil, Risk)  │
│    (Immediate re-calculation on objective switch; no fixed strategy)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             PHASE 10 & 12: SYNCHRONIZED INTELLIGENCE SUITES            │
│   (All 9 navigation views consume the SAME field; clean error banner)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 PHASE 14: RIGOROUS AUTOMATED TEST SUITE                │
│  (Pytest 18+ tests: invalid 975.04789 rejection, geocoding, Pareto)    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. IMMEDIATE ACTION PLAN

1. **Phase 1 & 2:** Implement `GeocodingService` in backend (`backend/app/services/geocoding_service.py`), add Pydantic coordinate validators to `schemas.py`, add client-side bounds clamping and address search in `MapPicker.tsx`, and synchronize `fieldName`, `county`, `state`, and `country`.
2. **Phase 3:** Create `DataAvailabilityService` (`backend/app/services/data_availability_service.py`) returning formal dataset availability records per location.
3. **Phase 8:** Upgrade `rotation_optimizer.py` and `RotationComparison.tsx` so toggling "Balanced", "Max Profit", "Soil Health", or "Resilience" triggers instant re-ranking and re-computation of the Pareto plans.
4. **Phase 12:** Fix error formatting in `frontend/src/api.ts` and `App.tsx` to completely eradicate `[object Object]` and invalidate stale field results when switching locations.
5. **Phase 14:** Add automated tests in `backend/tests/test_coordinate_and_geocoding.py` verifying coordinate rejection (`975.04789`), reverse geocoding, multi-location isolation, and dynamic rotation objective switching.
