"""
Aquora Water Quality Subsystem Router
Isolated inference endpoint for the 4-sensor ANN Water Quality Index pipeline.
Uses ONLY quality_* files.
"""

from pathlib import Path
from typing import Dict, Any, List
import logging

import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("aquora.quality")

router = APIRouter(prefix="/api/quality", tags=["Water Quality"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "quality_aquora_water_quality_ann_4sensor.joblib"

# Hardware Sensor Definitions
FEATURES = ["pH", "Turbidity_NTU", "TDS_mg_L", "Temperature_C"]

if not MODEL_PATH.exists():
    logger.error(f"Water Quality model not found at: {MODEL_PATH}")
    wq_pipeline = None
else:
    try:
        wq_pipeline = joblib.load(MODEL_PATH)
        logger.info(f"Loaded Water Quality ANN pipeline successfully from {MODEL_PATH.name}")
    except Exception as e:
        logger.error(f"Failed loading Water Quality model: {e}")
        wq_pipeline = None

# Hardware Sensor Benchmark Presets
PRESETS = {
    "optimal_potable": {
        "title": "Baseline Finished Tap Water",
        "description": "Typical municipal treated distribution water with balanced pH and low turbidity.",
        "sensors": {
            "pH": 7.4,
            "Turbidity_NTU": 0.8,
            "TDS_mg_L": 180.0,
            "Temperature_C": 19.5
        }
    },
    "turbid_runoff": {
        "title": "Stormwater Runoff / High Turbidity",
        "description": "Elevated particulate suspension and sediment influx following heavy rainfall event.",
        "sensors": {
            "pH": 6.7,
            "Turbidity_NTU": 16.5,
            "TDS_mg_L": 380.0,
            "Temperature_C": 22.0
        }
    },
    "high_tds_mineral": {
        "title": "High TDS / Hard Water Stream",
        "description": "High dissolved mineral salt concentration, groundwater intrusion profile.",
        "sensors": {
            "pH": 8.4,
            "Turbidity_NTU": 3.2,
            "TDS_mg_L": 890.0,
            "Temperature_C": 25.5
        }
    },
    "cold_alpine": {
        "title": "Cold Alpine Reservoir Inflow",
        "description": "Low-temperature, low-mineral mountain source reservoir telemetry.",
        "sensors": {
            "pH": 7.1,
            "Turbidity_NTU": 0.4,
            "TDS_mg_L": 65.0,
            "Temperature_C": 7.2
        }
    }
}

class WaterQualityRequest(BaseModel):
    pH: float = Field(..., ge=0.0, le=14.0, description="Acidity/Alkalinity index (0-14)")
    Turbidity_NTU: float = Field(..., ge=0.0, description="Nephelometric Turbidity Units")
    TDS_mg_L: float = Field(..., ge=0.0, description="Total Dissolved Solids in mg/L")
    Temperature_C: float = Field(..., ge=-10.0, le=60.0, description="Water temperature in degrees Celsius")

    class Config:
        json_schema_extra = {
            "example": {
                "pH": 7.2,
                "Turbidity_NTU": 1.5,
                "TDS_mg_L": 250.0,
                "Temperature_C": 21.0
            }
        }

@router.get("/info")
def get_model_info():
    """Return hardware specifications, evaluation metrics, and scientific research scope."""
    return {
        "subsystem": "Water Quality System",
        "model_artifact": "quality_aquora_water_quality_ann_4sensor.joblib",
        "architecture": "MLPRegressor inside sklearn Pipeline (SimpleImputer -> StandardScaler -> MLPRegressor)",
        "sensors": [
            {"id": "pH", "name": "pH Sensor", "unit": "pH", "typical_range": "6.5 - 8.5"},
            {"id": "Turbidity_NTU", "name": "Turbidity Sensor", "unit": "NTU", "typical_range": "0.1 - 5.0"},
            {"id": "TDS_mg_L", "name": "Total Dissolved Solids", "unit": "mg/L", "typical_range": "50 - 500"},
            {"id": "Temperature_C", "name": "Water Temperature", "unit": "°C", "typical_range": "5.0 - 30.0"}
        ],
        "validation_metrics": {
            "cv_5fold": {"R2": 0.581764, "RMSE": 3.100518, "MAE": 2.450033},
            "final_test": {"R2": 0.577137, "RMSE": 3.087164, "MAE": 2.434852}
        },
        "scientific_disclaimer": (
            "IMPORTANT SCIENTIFIC CONSTRAINT: This model estimates the dataset's empirical "
            "Water Quality Index (continuous numeric value). It contains NO Safe/Unsafe threshold, "
            "no contamination classification, no alarm classification, and no hardcoded status. "
            "Output represents an AI-estimated numeric regression index and not an independently "
            "certified contamination detection result."
        ),
        "presets": PRESETS
    }

@router.post("/predict")
def predict_water_quality(payload: WaterQualityRequest):
    """
    Computes AI-estimated Water Quality Index from the 4 physical sensors.
    Returns strictly a continuous numeric prediction without inventing safety categories.
    """
    if wq_pipeline is None:
        raise HTTPException(status_code=503, detail="Water Quality model artifact not loaded.")

    try:
        # Construct DataFrame preserving exact feature order
        input_df = pd.DataFrame([{
            "pH": payload.pH,
            "Turbidity_NTU": payload.Turbidity_NTU,
            "TDS_mg_L": payload.TDS_mg_L,
            "Temperature_C": payload.Temperature_C
        }], columns=FEATURES)

        raw_prediction = float(wq_pipeline.predict(input_df)[0])

        return {
            "success": True,
            "water_quality_index": round(raw_prediction, 3),
            "display_metric_title": "AI-estimated Water Quality Index",
            "sensors": {
                "pH": payload.pH,
                "Turbidity_NTU": payload.Turbidity_NTU,
                "TDS_mg_L": payload.TDS_mg_L,
                "Temperature_C": payload.Temperature_C
            },
            "scientific_note": (
                "Continuous numerical estimate from the 4-sensor ANN model. "
                "No safe/unsafe threshold is applied in compliance with project research guidelines."
            )
        }
    except Exception as e:
        logger.error(f"Prediction error in water quality router: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Water quality inference failed: {str(e)}")
