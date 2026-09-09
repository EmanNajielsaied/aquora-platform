"""
Aquora Platform HTTP Client
Encapsulates HTTP requests to the FastAPI backend service (default: http://localhost:8000).
"""

import os
from typing import Dict, Any, Optional
import requests

API_BASE_URL = os.environ.get("AQUORA_API_URL", "http://localhost:8000")

class AquoraAPIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def check_health(self) -> Dict[str, Any]:
        """Verify connection to backend and model status."""
        try:
            resp = requests.get(f"{self.base_url}/api/health", timeout=3.0)
            if resp.status_code == 200:
                return resp.json()
            return {"status": "error", "detail": f"Status code {resp.status_code}"}
        except Exception as e:
            return {"status": "offline", "detail": str(e)}

    # --- Water Quality Subsystem ---
    def get_water_quality_info(self) -> Dict[str, Any]:
        """Fetch model metadata and preset datasets."""
        resp = requests.get(f"{self.base_url}/api/quality/info", timeout=3.0)
        resp.raise_for_status()
        return resp.json()

    def predict_water_quality(self, payload: Dict[str, float]) -> Dict[str, Any]:
        """Compute AI-estimated Water Quality Index for 4 sensors."""
        resp = requests.post(f"{self.base_url}/api/quality/predict", json=payload, timeout=5.0)
        resp.raise_for_status()
        return resp.json()

    # --- Leak Detection Subsystem ---
    def get_leak_schema(self) -> Dict[str, Any]:
        """Fetch raw features, threshold, and presets for leak detection."""
        resp = requests.get(f"{self.base_url}/api/leak/schema", timeout=3.0)
        resp.raise_for_status()
        return resp.json()

    def get_leak_metrics(self) -> Dict[str, Any]:
        """Fetch model validation metrics."""
        resp = requests.get(f"{self.base_url}/api/leak/metrics", timeout=3.0)
        resp.raise_for_status()
        return resp.json()

    def predict_leak(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Run leak prediction pipeline."""
        resp = requests.post(f"{self.base_url}/api/leak/predict", json={"features": features}, timeout=5.0)
        resp.raise_for_status()
        return resp.json()

    # --- Decision System Subsystem ---
    def get_decision_schema(self) -> Dict[str, Any]:
        """Fetch 54 features schema and presets for decision system."""
        resp = requests.get(f"{self.base_url}/api/decision/schema", timeout=3.0)
        resp.raise_for_status()
        return resp.json()

    def get_decision_config(self) -> Dict[str, Any]:
        """Fetch expert score configuration and levels."""
        resp = requests.get(f"{self.base_url}/api/decision/config", timeout=3.0)
        resp.raise_for_status()
        return resp.json()

    def predict_decision(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Run 2-stage decision pipeline (ML failure prediction + Expert rules)."""
        resp = requests.post(f"{self.base_url}/api/decision/predict", json={"features": features}, timeout=5.0)
        resp.raise_for_status()
        return resp.json()

# Global default instance
api_client = AquoraAPIClient()
