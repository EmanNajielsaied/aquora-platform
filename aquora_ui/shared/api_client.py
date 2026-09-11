"""
Aquora Platform Unified Client
Supports dual-mode execution:
1. Direct In-Process ML Engine (Primary for Streamlit Community Cloud & single-container deployments)
2. HTTP REST Gateway (When connected to a dedicated external FastAPI server)
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import requests

# Ensure repository root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

logger = logging.getLogger("aquora.client")

# Direct in-process backend imports
try:
    from backend.app import health_check as backend_health_check
    from backend.routers import water_quality, leak_detection, decision_system
    DIRECT_AVAILABLE = True
except Exception as exc:
    logger.warning(f"Notice: Direct backend imports unavailable ({exc}). Relying on HTTP mode.")
    DIRECT_AVAILABLE = False

ENV_API_URL = os.environ.get("AQUORA_API_URL", "").strip()


class AquoraAPIClient:
    """
    Unified client providing seamless in-process ML inference for Streamlit Cloud
    while maintaining full HTTP REST capability when an external backend URL is specified.
    """

    def __init__(self, base_url: Optional[str] = None):
        url = base_url if base_url is not None else ENV_API_URL
        url = url.strip() if url else ""

        # Determine if caller explicitly targeted an external HTTP service
        self.is_explicit_external_http = bool(
            url and url.lower() != "direct" and not any(h in url for h in ["localhost", "127.0.0.1", "0.0.0.0"])
        )
        self.is_localhost_http = bool(
            url and any(h in url for h in ["localhost", "127.0.0.1", "0.0.0.0"])
        )

        if url and url.lower() != "direct":
            if not url.startswith(("http://", "https://")):
                url = f"http://{url}"
            self.base_url = url.rstrip("/")
        else:
            self.base_url = "http://localhost:8000"

        # Prefer direct execution if no remote external URL is configured and direct backend is ready
        self.prefer_direct = DIRECT_AVAILABLE and not self.is_explicit_external_http

    def check_health(self) -> Dict[str, Any]:
        """Verify connection and model statuses across all three subsystems."""
        # 1. If explicit external or localhost specified, attempt HTTP first
        if (self.is_explicit_external_http or self.is_localhost_http) and not self.prefer_direct:
            try:
                resp = requests.get(f"{self.base_url}/api/health", timeout=2.5)
                if resp.status_code == 200:
                    data = resp.json()
                    data["mode"] = "http"
                    return data
            except Exception as e:
                logger.debug(f"HTTP health check failed: {e}")

        # 2. In-process direct execution (Streamlit Cloud zero-latency native path)
        if DIRECT_AVAILABLE:
            try:
                data = backend_health_check()
                data["mode"] = "direct"
                return data
            except Exception as e:
                logger.error(f"Direct backend health check failed: {e}")
                return {"status": "error", "detail": f"Direct backend error: {e}"}

        # 3. Fallback HTTP attempt
        try:
            resp = requests.get(f"{self.base_url}/api/health", timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                data["mode"] = "http"
                return data
            return {"status": "error", "detail": f"Status code {resp.status_code}"}
        except Exception as e:
            return {"status": "offline", "detail": str(e)}

    # =========================================================================
    # 1. WATER QUALITY SUBSYSTEM
    # =========================================================================
    def get_water_quality_info(self) -> Dict[str, Any]:
        """Fetch water quality model metadata, sensor specs, and presets."""
        if self.prefer_direct:
            return water_quality.get_model_info()

        try:
            resp = requests.get(f"{self.base_url}/api/quality/info", timeout=5.0)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if DIRECT_AVAILABLE:
                return water_quality.get_model_info()
            raise e

    def predict_water_quality(self, payload: Dict[str, float]) -> Dict[str, Any]:
        """Compute AI-estimated numeric Water Quality Index for 4 sensors."""
        if self.prefer_direct:
            req = water_quality.WaterQualityRequest(
                pH=float(payload.get("pH", 7.0)),
                Turbidity_NTU=float(payload.get("Turbidity_NTU", 1.0)),
                TDS_mg_L=float(payload.get("TDS_mg_L", 200.0)),
                Temperature_C=float(payload.get("Temperature_C", 20.0))
            )
            return water_quality.predict_water_quality(req)

        try:
            resp = requests.post(f"{self.base_url}/api/quality/predict", json=payload, timeout=10.0)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if DIRECT_AVAILABLE:
                req = water_quality.WaterQualityRequest(
                    pH=float(payload.get("pH", 7.0)),
                    Turbidity_NTU=float(payload.get("Turbidity_NTU", 1.0)),
                    TDS_mg_L=float(payload.get("TDS_mg_L", 200.0)),
                    Temperature_C=float(payload.get("Temperature_C", 20.0))
                )
                return water_quality.predict_water_quality(req)
            raise e

    # =========================================================================
    # 2. LEAK DETECTION SUBSYSTEM
    # =========================================================================
    def get_leak_schema(self) -> Dict[str, Any]:
        """Fetch raw features, threshold (0.3880), and presets for leak detection."""
        if self.prefer_direct:
            return leak_detection.get_leak_schema()

        try:
            resp = requests.get(f"{self.base_url}/api/leak/schema", timeout=5.0)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if DIRECT_AVAILABLE:
                return leak_detection.get_leak_schema()
            raise e

    def get_leak_metrics(self) -> Dict[str, Any]:
        """Fetch leak detection model validation metrics."""
        if self.prefer_direct:
            return leak_detection.get_leak_metrics()

        try:
            resp = requests.get(f"{self.base_url}/api/leak/metrics", timeout=5.0)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if DIRECT_AVAILABLE:
                return leak_detection.get_leak_metrics()
            raise e

    def predict_leak(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run leak prediction pipeline (66 raw -> 82 features -> XGBoost -> threshold 0.3880)
        integrated with the supporting Expert System decision logic.
        """
        if self.prefer_direct:
            req = leak_detection.LeakPredictionRequest(features=features)
            return leak_detection.predict_leak(req)

        try:
            resp = requests.post(f"{self.base_url}/api/leak/predict", json={"features": features}, timeout=15.0)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if DIRECT_AVAILABLE:
                req = leak_detection.LeakPredictionRequest(features=features)
                return leak_detection.predict_leak(req)
            raise e

    # =========================================================================
    # 3. DECISION SYSTEM / PREDICTIVE MAINTENANCE SUBSYSTEM
    # =========================================================================
    def get_decision_schema(self) -> Dict[str, Any]:
        """Fetch 54 features schema, threshold (0.65), and presets for decision system."""
        if self.prefer_direct:
            return decision_system.get_decision_schema()

        try:
            resp = requests.get(f"{self.base_url}/api/decision/schema", timeout=5.0)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if DIRECT_AVAILABLE:
                return decision_system.get_decision_schema()
            raise e

    def get_decision_config(self) -> Dict[str, Any]:
        """Fetch expert score configuration and levels."""
        if self.prefer_direct:
            return decision_system.get_decision_config()

        try:
            resp = requests.get(f"{self.base_url}/api/decision/config", timeout=5.0)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if DIRECT_AVAILABLE:
                return decision_system.get_decision_config()
            raise e

    def predict_decision(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Run 2-stage decision pipeline (54 -> 71 features -> XGBoost 0.65 threshold + Expert heuristics)."""
        if self.prefer_direct:
            req = decision_system.DecisionPredictionRequest(features=features)
            return decision_system.predict_decision(req)

        try:
            resp = requests.post(f"{self.base_url}/api/decision/predict", json={"features": features}, timeout=15.0)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if DIRECT_AVAILABLE:
                req = decision_system.DecisionPredictionRequest(features=features)
                return decision_system.predict_decision(req)
            raise e


# Global default client instance
api_client = AquoraAPIClient()
