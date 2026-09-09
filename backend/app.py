"""
Aquora Water Infrastructure Platform - Unified Backend API
Serves three isolated subsystems:
1. Water Quality System (ANN 4-sensor WQI continuous regression)
2. Leak Detection System (XGBoost 66->82 pipeline with threshold 0.3880)
3. Expert System / Decision Logic (XGBoost 54->71 ML failure prob + Expert heuristic rule layer)
"""

import datetime
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routers import water_quality, leak_detection, decision_system

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("aquora.api")

app = FastAPI(
    title="Aquora Smart Water Infrastructure API",
    description=(
        "Unified research & operational API for water quality monitoring, "
        "leak detection, and expert decision-support systems."
    ),
    version="2.0.0"
)

# Enable CORS for frontend and external integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount isolated routers
app.include_router(water_quality.router)
app.include_router(leak_detection.router)
app.include_router(decision_system.router)

@app.get("/api/health")
def health_check():
    """Unified health check endpoint auditing all three subsystem models."""
    wq_loaded = water_quality.wq_pipeline is not None
    leak_loaded = (leak_detection.leak_model is not None and leak_detection.leak_preprocessor is not None)
    decision_loaded = (decision_system.decision_model is not None and decision_system.decision_preprocessor is not None)

    all_healthy = wq_loaded and leak_loaded and decision_loaded

    return {
        "status": "online" if all_healthy else "degraded",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "subsystems": {
            "water_quality": {
                "name": "Water Quality ANN",
                "status": "ready" if wq_loaded else "unavailable",
                "features": 4,
                "sensors": ["pH", "Turbidity_NTU", "TDS_mg_L", "Temperature_C"],
                "target": "Water_Quality_Index (Continuous Numeric)"
            },
            "leak_detection": {
                "name": "Leak Detection XGBoost",
                "status": "ready" if leak_loaded else "unavailable",
                "raw_features": len(leak_detection.RAW_FEATURES),
                "transformed_features": 82,
                "threshold": leak_detection.THRESHOLD,
                "target": "Leak_No_Leak"
            },
            "decision_system": {
                "name": "Expert System & Predictive Maintenance",
                "status": "ready" if decision_loaded else "unavailable",
                "raw_features": len(decision_system.ALL_FEATURES),
                "transformed_features": 71,
                "ml_threshold": decision_system.ML_THRESHOLD,
                "target": "Failure_Next_30_Days + Expert Decision Layer"
            }
        }
    }

@app.get("/")
def root_info():
    """Welcome index with service catalog and documentation links."""
    return {
        "message": "Welcome to Aquora Smart Water Infrastructure API",
        "subsystems": [
            {"id": "quality", "title": "Water Quality (ANN 4-Sensor)", "endpoint": "/api/quality"},
            {"id": "leak", "title": "Leak Detection (XGBoost 66-Feature)", "endpoint": "/api/leak"},
            {"id": "decision", "title": "Decision System & Expert Logic", "endpoint": "/api/decision"}
        ],
        "interactive_docs": "/docs",
        "openapi_schema": "/openapi.json"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
