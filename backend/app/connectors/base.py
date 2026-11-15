"""
FARMINTEL AI - Base Data Connector
Standardizes HTTP requests, retry logic, caching, provenance tracking, and error handling.
"""

import time
import requests
from typing import Dict, Any, Optional
from ..database import generate_cache_key, get_cached_response, set_cached_response

class ConnectorResult:
    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        cached: bool = False,
        latency_ms: float = 0.0,
        status_code: int = 200,
        error: Optional[str] = None,
        source: str = "",
        provenance: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.data = data or {}
        self.cached = cached
        self.latency_ms = latency_ms
        self.status_code = status_code
        self.error = error
        self.source = source
        self.provenance = provenance or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "cached": self.cached,
            "latency_ms": round(self.latency_ms, 2),
            "status_code": self.status_code,
            "error": self.error,
            "source": self.source,
            "provenance": self.provenance
        }

class BaseConnector:
    def __init__(self, source_name: str, base_url: str, default_timeout: int = 30):
        self.source_name = source_name
        self.base_url = base_url
        self.default_timeout = default_timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "FARMINTEL-AI/1.0 (NASA Space Apps Challenge; contact@farmintel.ai)"
        })

    def get(
        self,
        endpoint: str = "",
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> ConnectorResult:
        url = f"{self.base_url}{endpoint}" if endpoint else self.base_url
        cache_key = generate_cache_key(self.source_name, url, params)

        if use_cache:
            cached_data = get_cached_response(cache_key)
            if cached_data is not None:
                return ConnectorResult(
                    success=True,
                    data=cached_data,
                    cached=True,
                    latency_ms=0.5,
                    status_code=200,
                    source=self.source_name,
                    provenance={"cache_hit": True, "source_url": url}
                )

        start_time = time.time()
        timeout_val = timeout or self.default_timeout
        try:
            resp = self.session.get(url, params=params, headers=headers, timeout=timeout_val)
            latency = (time.time() - start_time) * 1000

            if resp.status_code == 200:
                try:
                    json_data = resp.json()
                    if use_cache:
                        set_cached_response(cache_key, self.source_name, url, params, json_data)
                    return ConnectorResult(
                        success=True,
                        data=json_data,
                        cached=False,
                        latency_ms=latency,
                        status_code=resp.status_code,
                        source=self.source_name,
                        provenance={"source_url": resp.url, "timestamp": time.time()}
                    )
                except Exception as json_err:
                    return ConnectorResult(
                        success=False,
                        error=f"JSON parsing error: {str(json_err)}",
                        latency_ms=latency,
                        status_code=resp.status_code,
                        source=self.source_name
                    )
            else:
                return ConnectorResult(
                    success=False,
                    error=f"HTTP {resp.status_code}: {resp.text[:300]}",
                    latency_ms=latency,
                    status_code=resp.status_code,
                    source=self.source_name
                )
        except requests.exceptions.Timeout:
            latency = (time.time() - start_time) * 1000
            return ConnectorResult(
                success=False,
                error=f"Request timed out after {timeout_val}s",
                latency_ms=latency,
                status_code=504,
                source=self.source_name
            )
        except requests.exceptions.RequestException as req_err:
            latency = (time.time() - start_time) * 1000
            return ConnectorResult(
                success=False,
                error=f"Network error: {str(req_err)}",
                latency_ms=latency,
                status_code=500,
                source=self.source_name
            )
