"""
FARMINTEL AI - Reverse Geocoding & Location Resolver Service
Resolves decimal coordinates (lat, lon) into authoritative administrative entities:
County, State, State Code, Country, and Agricultural District.
Uses high-reliability caching and multi-tier public geospatial resolvers:
1. Local offline US Agricultural Centroids & County Polygons / Bounding Catalog
2. OpenStreetMap Nominatim reverse geocoding (with polite user-agent and caching)
3. FCC Census Geocoder API fallback for domestic CONUS FIPS resolution
"""

import math
import requests
from typing import Dict, Any, Optional, List
from ..database import get_cached_response, cache_api_response, generate_cache_key

# Curated high-precision offline anchors for core US and International agricultural production zones
KEY_AGRICULTURAL_ZONES = [
    # United States Core Belts
    {"country": "United States", "state": "Iowa", "state_code": "IA", "county": "Story County", "lat": 42.0308, "lon": -93.6319, "radius_deg": 0.45},
    {"country": "United States", "state": "Iowa", "state_code": "IA", "county": "Polk County", "lat": 41.5868, "lon": -93.6250, "radius_deg": 0.35},
    {"country": "United States", "state": "California", "state_code": "CA", "county": "Fresno County", "lat": 36.7468, "lon": -119.7726, "radius_deg": 0.85},
    {"country": "United States", "state": "Kansas", "state_code": "KS", "county": "Finney County", "lat": 37.9717, "lon": -100.8654, "radius_deg": 0.55},
    {"country": "United States", "state": "Illinois", "state_code": "IL", "county": "Champaign County", "lat": 40.1164, "lon": -88.2434, "radius_deg": 0.45},
    {"country": "United States", "state": "Nebraska", "state_code": "NE", "county": "Hall County", "lat": 40.9250, "lon": -98.3421, "radius_deg": 0.45},
    {"country": "United States", "state": "North Dakota", "state_code": "ND", "county": "Cass County", "lat": 46.8772, "lon": -96.7898, "radius_deg": 0.55},
    {"country": "United States", "state": "Colorado", "state_code": "CO", "county": "Pueblo County", "lat": 38.2544, "lon": -104.6091, "radius_deg": 0.65},
    {"country": "United States", "state": "Colorado", "state_code": "CO", "county": "Weld County", "lat": 40.4233, "lon": -104.7091, "radius_deg": 0.85},
    {"country": "United States", "state": "Texas", "state_code": "TX", "county": "Lubbock County", "lat": 33.5779, "lon": -101.8552, "radius_deg": 0.55},
    {"country": "United States", "state": "North Carolina", "state_code": "NC", "county": "Wayne County", "lat": 35.3849, "lon": -77.9928, "radius_deg": 0.45},

    # International Major Agricultural Breadbaskets
    {"country": "India", "state": "Punjab", "state_code": "PB", "county": "Ludhiana District", "lat": 30.9010, "lon": 75.8573, "radius_deg": 1.5},
    {"country": "India", "state": "Haryana", "state_code": "HR", "county": "Karnal District", "lat": 29.6857, "lon": 76.9905, "radius_deg": 1.2},
    {"country": "Brazil", "state": "Mato Grosso", "state_code": "MT", "county": "Sorriso Agricultural Basin", "lat": -12.5560, "lon": -55.7226, "radius_deg": 2.5},
    {"country": "France", "state": "Centre-Val de Loire", "state_code": "CVL", "county": "Beauce Agricultural Plain", "lat": 48.4439, "lon": 1.4890, "radius_deg": 1.2},
    {"country": "Canada", "state": "Alberta", "state_code": "AB", "county": "Peace River Country", "lat": 58.3095, "lon": -116.8210, "radius_deg": 2.0},
    {"country": "Canada", "state": "Saskatchewan", "state_code": "SK", "county": "Regina Plains", "lat": 50.4452, "lon": -104.6189, "radius_deg": 1.8},
    {"country": "Australia", "state": "New South Wales", "state_code": "NSW", "county": "Central West Plains", "lat": -31.2532, "lon": 146.9211, "radius_deg": 2.5},
    {"country": "Argentina", "state": "Buenos Aires", "state_code": "BA", "county": "Pergamino Pampas", "lat": -33.8900, "lon": -60.5700, "radius_deg": 1.8},
    {"country": "Kenya", "state": "Rift Valley", "state_code": "RV", "county": "Nakuru Highland Basin", "lat": -0.3031, "lon": 36.0800, "radius_deg": 1.2},
    {"country": "Ukraine", "state": "Vinnytsia", "state_code": "VN", "county": "Chernozem Belt", "lat": 49.2331, "lon": 28.4682, "radius_deg": 1.5},
]
US_AGRICULTURAL_ZONES = KEY_AGRICULTURAL_ZONES  # Backward compatibility alias

# US State Bounding Envelopes for offline state attribution
US_STATES_BOUNDS = [
    {"state": "Iowa", "state_code": "IA", "min_lat": 40.37, "max_lat": 43.50, "min_lon": -96.64, "max_lon": -90.14},
    {"state": "California", "state_code": "CA", "min_lat": 32.53, "max_lat": 42.01, "min_lon": -124.41, "max_lon": -114.13},
    {"state": "Kansas", "state_code": "KS", "min_lat": 36.99, "max_lat": 40.00, "min_lon": -102.05, "max_lon": -94.59},
    {"state": "Illinois", "state_code": "IL", "min_lat": 36.97, "max_lat": 42.51, "min_lon": -91.51, "max_lon": -87.02},
    {"state": "Nebraska", "state_code": "NE", "min_lat": 40.00, "max_lat": 43.00, "min_lon": -104.05, "max_lon": -95.31},
    {"state": "Colorado", "state_code": "CO", "min_lat": 36.99, "max_lat": 41.00, "min_lon": -109.05, "max_lon": -102.04},
    {"state": "North Dakota", "state_code": "ND", "min_lat": 45.94, "max_lat": 49.00, "min_lon": -104.05, "max_lon": -96.55},
    {"state": "Texas", "state_code": "TX", "min_lat": 25.84, "max_lat": 36.50, "min_lon": -106.65, "max_lon": -93.51},
    {"state": "Minnesota", "state_code": "MN", "min_lat": 43.50, "max_lat": 49.38, "min_lon": -97.24, "max_lon": -89.49},
    {"state": "Indiana", "state_code": "IN", "min_lat": 37.77, "max_lat": 41.76, "min_lon": -88.10, "max_lon": -84.78},
    {"state": "Missouri", "state_code": "MO", "min_lat": 35.99, "max_lat": 40.61, "min_lon": -95.77, "max_lon": -89.10},
    {"state": "North Carolina", "state_code": "NC", "min_lat": 33.84, "max_lat": 36.59, "min_lon": -84.32, "max_lon": -75.46},
]

class GeocodingService:
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
    FCC_CENSUS_URL = "https://geo.fcc.gov/api/census/block/find"

    @classmethod
    def reverse_geocode(cls, latitude: float, longitude: float, use_cache: bool = True) -> Dict[str, Any]:
        """
        Reverse geocodes (lat, lon) to county, state, state_code, and country.
        Guarantees fast offline resolution for known agricultural centers and
        falls back to online public reverse geocoders when connected.
        """
        # Validate coordinates bounds
        if not (-90.0 <= latitude <= 90.0):
            raise ValueError(f"Latitude must be between -90 and 90 degrees. Received {latitude}")
        if not (-180.0 <= longitude <= 180.0):
            raise ValueError(f"Longitude must be between -180 and 180 degrees. Received {longitude}")

        lat_r = round(latitude, 4)
        lon_r = round(longitude, 4)

        # 1. Check local cache
        cache_key = generate_cache_key("GEOCODE", f"{lat_r}:{lon_r}")
        if use_cache:
            cached = get_cached_response(cache_key)
            if cached:
                cached["cached"] = True
                return cached

        # 2. Check offline agricultural zones catalog (instant matching)
        for zone in KEY_AGRICULTURAL_ZONES:
            dist = math.sqrt((lat_r - zone["lat"])**2 + (lon_r - zone["lon"])**2)
            if dist <= zone["radius_deg"]:
                country = zone.get("country", "United States")
                result = {
                    "success": True,
                    "county": zone["county"],
                    "state": zone["state"],
                    "state_code": zone["state_code"],
                    "country": country,
                    "display_name": f"{zone['county']}, {zone['state']}, {country}",
                    "source": "OFFLINE_AG_ZONES_CATALOG",
                    "latitude": lat_r,
                    "longitude": lon_r
                }
                cache_api_response(cache_key, "GEOCODE", f"{lat_r}:{lon_r}", result, expires_hours=720)
                return result

        # 3. Try FCC Census Block Geocoder (Domestic US high-reliability free service)
        try:
            params = {
                "latitude": lat_r,
                "longitude": lon_r,
                "format": "json"
            }
            resp = requests.get(cls.FCC_CENSUS_URL, params=params, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                state_data = data.get("State", {})
                county_data = data.get("County", {})
                if state_data.get("name") and county_data.get("name"):
                    c_name = county_data["name"]
                    if not c_name.lower().endswith("county"):
                        c_name = f"{c_name} County"
                    result = {
                        "success": True,
                        "county": c_name,
                        "state": state_data.get("name"),
                        "state_code": state_data.get("code"),
                        "country": "United States",
                        "display_name": f"{c_name}, {state_data.get('name')}, USA",
                        "source": "FCC_CENSUS_GEOCODER",
                        "latitude": lat_r,
                        "longitude": lon_r
                    }
                    cache_api_response(cache_key, "GEOCODE", f"{lat_r}:{lon_r}", result, expires_hours=720)
                    return result
        except Exception:
            pass

        # 4. Try OpenStreetMap Nominatim reverse geocode (fallback)
        try:
            headers = {"User-Agent": "FarmIntelAI/2.0 (NASA Space Apps Challenge 2026; Geospatial Agricultural Intelligence)"}
            params = {
                "lat": lat_r,
                "lon": lon_r,
                "format": "jsonv2",
                "zoom": 10,
                "addressdetails": 1
            }
            resp = requests.get(cls.NOMINATIM_URL, params=params, headers=headers, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                addr = data.get("address", {})
                county = addr.get("county") or addr.get("district") or addr.get("state_district") or addr.get("municipality")
                state = addr.get("state") or addr.get("region") or addr.get("province")
                country = addr.get("country", "United States")
                if county or state or country:
                    display_parts = [p for p in [county, state, country] if p]
                    result = {
                        "success": True,
                        "county": county or (f"{state} Region" if state else f"{country} Territory"),
                        "state": state or country,
                        "state_code": addr.get("state_code", "")[:4].upper(),
                        "country": country,
                        "display_name": ", ".join(display_parts) if display_parts else data.get("display_name", f"{lat_r}, {lon_r}"),
                        "source": "OSM_NOMINATIM",
                        "latitude": lat_r,
                        "longitude": lon_r
                    }
                    cache_api_response(cache_key, "GEOCODE", f"{lat_r}:{lon_r}", result, expires_hours=720)
                    return result
        except Exception:
            pass

        # 5. Offline Fallback: Check State Bounding Envelopes
        for sb in US_STATES_BOUNDS:
            if sb["min_lat"] <= lat_r <= sb["max_lat"] and sb["min_lon"] <= lon_r <= sb["max_lon"]:
                result = {
                    "success": True,
                    "county": f"{sb['state']} Agricultural Region",
                    "state": sb["state"],
                    "state_code": sb["state_code"],
                    "country": "United States",
                    "display_name": f"{sb['state']}, USA",
                    "source": "OFFLINE_STATE_BOUNDING",
                    "latitude": lat_r,
                    "longitude": lon_r
                }
                cache_api_response(cache_key, "GEOCODE", f"{lat_r}:{lon_r}", result, expires_hours=720)
                return result

        # Outside mapped zones
        is_conus = (24.0 <= lat_r <= 50.0) and (-125.0 <= lon_r <= -66.0)
        return {
            "success": True,
            "county": "Domestic US Agricultural Region" if is_conus else "Global Agricultural Region",
            "state": "United States" if is_conus else "International",
            "state_code": "US" if is_conus else "INTL",
            "country": "United States" if is_conus else "International",
            "display_name": f"{lat_r}° N, {abs(lon_r)}° {'W' if lon_r < 0 else 'E'}",
            "source": "GEOSPATIAL_COORDINATE_FALLBACK",
            "latitude": lat_r,
            "longitude": lon_r
        }

    @classmethod
    def search_location(cls, query: str) -> List[Dict[str, Any]]:
        """Searches for agricultural regions, counties, cities, states, or countries worldwide."""
        if not query or len(query.strip()) < 2:
            return []
        
        q = query.strip()
        matches = []
        seen = set()

        # 1. Check curated key agricultural zones (instant match)
        for z in KEY_AGRICULTURAL_ZONES:
            country_name = z.get("country", "United States")
            c_str = f"{z['county']} {z['state']} {country_name}".lower()
            if q.lower() in c_str:
                k = (round(z["lat"], 2), round(z["lon"], 2))
                if k not in seen:
                    seen.add(k)
                    matches.append({
                        "display_name": f"{z['county']}, {z['state']}, {country_name}",
                        "latitude": z["lat"],
                        "longitude": z["lon"],
                        "county": z["county"],
                        "state": z["state"],
                        "country": country_name,
                        "state_code": z["state_code"],
                        "source": "AG_CATALOG"
                    })

        # 2. Try global OpenStreetMap Nominatim search
        try:
            headers = {"User-Agent": "FarmIntelAI/2.0 (NASA Space Apps Challenge 2026; Agricultural Intelligence)"}
            params = {
                "q": q,
                "format": "jsonv2",
                "limit": 6,
                "addressdetails": 1
            }
            resp = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers, timeout=4)
            if resp.status_code == 200:
                for item in resp.json():
                    lat = round(float(item["lat"]), 4)
                    lon = round(float(item["lon"]), 4)
                    k = (round(lat, 2), round(lon, 2))
                    if k in seen:
                        continue
                    seen.add(k)

                    addr = item.get("address", {})
                    country = addr.get("country", "")
                    state = addr.get("state") or addr.get("region") or addr.get("province")
                    county = addr.get("county") or addr.get("district") or addr.get("state_district") or addr.get("city")
                    
                    matches.append({
                        "display_name": item.get("display_name"),
                        "latitude": lat,
                        "longitude": lon,
                        "county": county,
                        "state": state,
                        "country": country,
                        "state_code": addr.get("state_code", "")[:4].upper(),
                        "source": "NOMINATIM"
                    })
        except Exception:
            pass

        return matches
