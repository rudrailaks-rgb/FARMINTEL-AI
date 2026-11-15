"""
FARMINTEL AI - Database and Request Cache Persistence (SQLite)
Designed for seamless future migration to PostgreSQL / PostGIS.
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
from .config import settings

def get_connection():
    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. API Cache Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_cache (
            cache_key TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            request_url TEXT NOT NULL,
            request_params TEXT,
            response_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
    """)
    
    # 2. Field Analysis History Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS field_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            region TEXT NOT NULL,
            state TEXT NOT NULL,
            analysis_summary TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 3. Dataset Registry Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dataset_registry (
            dataset_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source_agency TEXT NOT NULL,
            status TEXT NOT NULL,
            last_checked TIMESTAMP,
            latency_ms REAL,
            record_count INTEGER DEFAULT 0,
            error_message TEXT,
            metadata_json TEXT
        )
    """)

    # 4. Satellite Observations Table (Phase 4 Real Raster Persistence)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS satellite_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field_id TEXT NOT NULL,
            dataset_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            scene_id TEXT NOT NULL,
            acquisition_date TEXT NOT NULL,
            observation_period TEXT,
            spatial_resolution REAL,
            calculated_indicators TEXT NOT NULL,
            valid_pixel_coverage REAL NOT NULL,
            quality_metadata TEXT NOT NULL,
            retrieval_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def generate_cache_key(source: str, url: str, params: Optional[Dict[str, Any]] = None) -> str:
    serialized = f"{source}:{url}:{json.dumps(params or {}, sort_keys=True)}"
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

def get_cached_response(cache_key: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT response_data FROM api_cache WHERE cache_key = ?", (cache_key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        try:
            return json.loads(row["response_data"])
        except Exception:
            return None
    return None

def set_cached_response(cache_key: str, source: str, url: str, params: Optional[Any] = None, data: Optional[Dict[str, Any]] = None, expires_hours: Optional[int] = None, **kwargs):
    if data is None and isinstance(params, dict):
        data = params
        params = {}
    elif data is None:
        data = {"value": params}
        params = {}
    
    expires_at = None
    if expires_hours:
        from datetime import timedelta
        expires_at = (datetime.utcnow() + timedelta(hours=expires_hours)).isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO api_cache (cache_key, source, request_url, request_params, response_data, created_at, expires_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        cache_key,
        source,
        url,
        json.dumps(params or {}),
        json.dumps(data or {}),
        datetime.utcnow().isoformat(),
        expires_at
    ))
    conn.commit()
    conn.close()

# Alias for backward compatibility
cache_api_response = set_cached_response

def save_field_analysis(field_name: str, latitude: float, longitude: float, region: str, state: str, analysis_summary: Dict[str, Any]):
    """Persists a field evaluation record to SQLite for session history."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO field_analyses (field_name, latitude, longitude, region, state, analysis_summary, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            field_name,
            latitude,
            longitude,
            region,
            state,
            json.dumps(analysis_summary),
            datetime.utcnow().isoformat()
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Warning: Failed to save field analysis to database: {e}")

def get_recent_field_analyses(limit: int = 10) -> list:
    """Retrieves recent field evaluation runs."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, field_name, latitude, longitude, region, state, created_at FROM field_analyses ORDER BY id DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
    except Exception:
        return []

def save_satellite_observation(
    field_id: str,
    dataset_id: str,
    product_id: str,
    scene_id: str,
    acquisition_date: str,
    observation_period: str,
    spatial_resolution: float,
    calculated_indicators: Dict[str, Any],
    valid_pixel_coverage: float,
    quality_metadata: Dict[str, Any]
):
    """Persists real satellite raster indicators (NDVI, valid pixels, quality flags) to SQLite."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO satellite_observations (
                field_id, dataset_id, product_id, scene_id, acquisition_date,
                observation_period, spatial_resolution, calculated_indicators,
                valid_pixel_coverage, quality_metadata, retrieval_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            field_id,
            dataset_id,
            product_id,
            scene_id,
            acquisition_date,
            observation_period,
            spatial_resolution,
            json.dumps(calculated_indicators),
            valid_pixel_coverage,
            json.dumps(quality_metadata),
            datetime.utcnow().isoformat()
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Warning: Failed to save satellite observation: {e}")

def get_recent_satellite_observations(limit: int = 10) -> list:
    """Retrieves recent satellite raster observations from SQLite."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, field_id, dataset_id, product_id, scene_id, acquisition_date,
                   observation_period, spatial_resolution, calculated_indicators,
                   valid_pixel_coverage, quality_metadata, retrieval_timestamp
            FROM satellite_observations ORDER BY id DESC LIMIT ?
        """, (limit,))
        rows = []
        for r in cursor.fetchall():
            d = dict(r)
            d["calculated_indicators"] = json.loads(d["calculated_indicators"])
            d["quality_metadata"] = json.loads(d["quality_metadata"])
            rows.append(d)
        conn.close()
        return rows
    except Exception:
        return []

init_db()
