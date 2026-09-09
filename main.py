import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import datetime

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("powerguard")

BASE_DIR = Path(__file__).resolve().parent

# File paths
MODEL_PATH = BASE_DIR / "xgboost_model.pkl"
PREPROCESSOR_PATH = BASE_DIR / "preprocessor.pkl"
SCHEMA_PATH = BASE_DIR / "input_schema.json"
THRESHOLDS_PATH = BASE_DIR / "thresholds.json"
STATIC_DIR = BASE_DIR / "static"

# Load schema and thresholds
if not SCHEMA_PATH.exists():
    raise FileNotFoundError(f"Input schema file not found: {SCHEMA_PATH}")

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    SCHEMA = json.load(f)

ALL_FEATURES: List[str] = SCHEMA["features"]
NUMERIC_FEATURES: List[str] = SCHEMA["numeric_features"]
CATEGORICAL_FEATURES: List[str] = SCHEMA["categorical_features"]
CATEGORICAL_VALUES: Dict[str, List[str]] = SCHEMA["categorical_values"]

THRESHOLD = 0.65
if THRESHOLDS_PATH.exists():
    with open(THRESHOLDS_PATH, "r", encoding="utf-8") as f:
        thresholds_data = json.load(f)
        THRESHOLD = float(thresholds_data.get("XGBoost", 0.65))

logger.info(f"Loaded schema with {len(ALL_FEATURES)} features ({len(NUMERIC_FEATURES)} numeric, {len(CATEGORICAL_FEATURES)} categorical).")
logger.info(f"Loaded decision threshold for XGBoost: {THRESHOLD}")

# Load Preprocessor and Model
if not PREPROCESSOR_PATH.exists():
    raise FileNotFoundError(f"Preprocessor file not found: {PREPROCESSOR_PATH}")
if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

preprocessor = joblib.load(PREPROCESSOR_PATH)
xgboost_model = joblib.load(MODEL_PATH)

logger.info("Successfully loaded preprocessor and XGBoost model into memory.")

# Define Feature Groups for UI structure
FEATURE_GROUPS = [
    {
        "id": "group_infrastructure",
        "title": "Asset & Pipe Specifications",
        "icon": "building-pipelines",
        "description": "Physical parameters, material properties, and operational classification",
        "features": [
            "Asset_Type", "Pipe_Material", "Pipe_Diameter_cm", "Pipe_Length_m", 
            "Pipe_Depth_m", "Frost_Depth_m", "Pipe_Age_Years", "Condition_Score", 
            "Criticality", "Criticality_Score"
        ]
    },
    {
        "id": "group_configuration",
        "title": "Pipe Configuration Flags",
        "icon": "toggle-right",
        "description": "Binary state indicators for pipe treatment, lining, and dimension status",
        "features": [
            "Lined", "Undersized", "Shallow_Main", "Oversized", "Cleaned"
        ]
    },
    {
        "id": "group_hydraulics",
        "title": "Hydraulic & Operational Metrics",
        "icon": "activity",
        "description": "Real-time flow, pressure dynamics, demand volume, and tank levels",
        "features": [
            "Pressure", "Flow_Rate", "Pressure_Deviation", "Flow_Deviation", 
            "Pressure_Change_Rate", "Flow_Change_Rate", "Pressure_Flow_Ratio", 
            "Water_Demand", "Tank_Level"
        ]
    },
    {
        "id": "group_environment",
        "title": "Environmental & Time Context",
        "icon": "sun-cloud",
        "description": "Ambient temperature, temporal features, day of week, and seasonal factors",
        "features": [
            "Temperature_C", "Year", "Month", "Day", "Hour", "Day_of_Week", "Season"
        ]
    },
    {
        "id": "group_maintenance",
        "title": "Maintenance & Historical Failures",
        "icon": "history",
        "description": "Historical failure frequency, elapsed time since incident, and record flags",
        "features": [
            "Previous_Failures", "Failures_Last_1_Year", "Failures_Last_3_Years", 
            "Days_Since_Last_Failure", "Days_Since_Last_Failure_Was_Missing"
        ]
    },
    {
        "id": "group_vibration",
        "title": "Vibration Sensor Telemetry",
        "icon": "radio-wave",
        "description": "High-frequency vibration statistical metrics (RMS, Energy, Kurtosis)",
        "features": [
            "Vibration_RMS", "Vibration_STD", "Vibration_Min", "Vibration_Max", 
            "Vibration_PeakToPeak", "Vibration_Energy", "Vibration_Kurtosis", "Vibration_Skewness"
        ]
    },
    {
        "id": "group_acoustic",
        "title": "Acoustic Sensor Telemetry",
        "icon": "sound-wave",
        "description": "Acoustic emission telemetry metrics for micro-leak and stress detection",
        "features": [
            "Acoustic_RMS", "Acoustic_STD", "Acoustic_Min", "Acoustic_Max", 
            "Acoustic_PeakToPeak", "Acoustic_Energy", "Acoustic_Kurtosis", "Acoustic_Skewness"
        ]
    },
    {
        "id": "group_risk",
        "title": "Risk & Anomaly Indicators",
        "icon": "alert-triangle",
        "description": "Composite asset risk score and automated sensor anomaly index",
        "features": [
            "Sensor_Anomaly_Score", "Asset_Risk_Score"
        ]
    }
]

# Baseline preset templates
PRESETS = {
    "normal": {
        "title": "Normal Asset (Low Risk)",
        "description": "Newly inspected main pipe operating under optimal pressure and low vibration.",
        "data": {
            "Asset_Type": "MAIN",
            "Pipe_Material": "DI",
            "Pipe_Diameter_cm": 30.0,
            "Pipe_Length_m": 120.0,
            "Pipe_Depth_m": 1.8,
            "Frost_Depth_m": 0.8,
            "Pipe_Age_Years": 5.0,
            "Condition_Score": 8.5,
            "Criticality": "Medium",
            "Criticality_Score": 4.0,
            "Lined": 1,
            "Undersized": 0,
            "Shallow_Main": 0,
            "Oversized": 0,
            "Cleaned": 1,
            "Pressure": 4.2,
            "Flow_Rate": 45.0,
            "Pressure_Deviation": 0.05,
            "Flow_Deviation": 0.1,
            "Pressure_Change_Rate": 0.01,
            "Flow_Change_Rate": 0.02,
            "Pressure_Flow_Ratio": 0.0933,
            "Temperature_C": 18.5,
            "Year": 2026,
            "Month": 9,
            "Day": 6,
            "Hour": 14,
            "Day_of_Week": "Sunday",
            "Season": "Autumn",
            "Previous_Failures": 0,
            "Failures_Last_1_Year": 0,
            "Failures_Last_3_Years": 0,
            "Days_Since_Last_Failure": 1825.0,
            "Days_Since_Last_Failure_Was_Missing": 0,
            "Vibration_RMS": 0.12,
            "Vibration_STD": 0.03,
            "Vibration_Min": 0.05,
            "Vibration_Max": 0.22,
            "Vibration_PeakToPeak": 0.17,
            "Vibration_Energy": 0.014,
            "Vibration_Kurtosis": 2.8,
            "Vibration_Skewness": 0.1,
            "Acoustic_RMS": 0.15,
            "Acoustic_STD": 0.04,
            "Acoustic_Min": 0.08,
            "Acoustic_Max": 0.28,
            "Acoustic_PeakToPeak": 0.20,
            "Acoustic_Energy": 0.022,
            "Acoustic_Kurtosis": 2.9,
            "Acoustic_Skewness": 0.15,
            "Sensor_Anomaly_Score": 0.05,
            "Asset_Risk_Score": 0.12,
            "Water_Demand": 150.0,
            "Tank_Level": 7.5
        }
    },
    "high_risk": {
        "title": "High-Risk Asset (Failure Expected)",
        "description": "Aging unlined cast-iron pipe with high pressure fluctuations, elevated vibration, and past failures.",
        "data": {
            "Asset_Type": "MAIN",
            "Pipe_Material": "CI",
            "Pipe_Diameter_cm": 15.0,
            "Pipe_Length_m": 250.0,
            "Pipe_Depth_m": 0.9,
            "Frost_Depth_m": 1.2,
            "Pipe_Age_Years": 55.0,
            "Condition_Score": 2.1,
            "Criticality": "Critical",
            "Criticality_Score": 9.5,
            "Lined": 0,
            "Undersized": 1,
            "Shallow_Main": 1,
            "Oversized": 0,
            "Cleaned": 0,
            "Pressure": 8.5,
            "Flow_Rate": 12.0,
            "Pressure_Deviation": 2.8,
            "Flow_Deviation": 3.4,
            "Pressure_Change_Rate": 0.85,
            "Flow_Change_Rate": 0.92,
            "Pressure_Flow_Ratio": 0.708,
            "Temperature_C": -2.0,
            "Year": 2026,
            "Month": 1,
            "Day": 15,
            "Hour": 3,
            "Day_of_Week": "Thursday",
            "Season": "Winter",
            "Previous_Failures": 5,
            "Failures_Last_1_Year": 2,
            "Failures_Last_3_Years": 4,
            "Days_Since_Last_Failure": 42.0,
            "Days_Since_Last_Failure_Was_Missing": 0,
            "Vibration_RMS": 1.85,
            "Vibration_STD": 0.65,
            "Vibration_Min": 0.40,
            "Vibration_Max": 3.90,
            "Vibration_PeakToPeak": 3.50,
            "Vibration_Energy": 3.42,
            "Vibration_Kurtosis": 8.2,
            "Vibration_Skewness": 2.1,
            "Acoustic_RMS": 2.10,
            "Acoustic_STD": 0.75,
            "Acoustic_Min": 0.50,
            "Acoustic_Max": 4.50,
            "Acoustic_PeakToPeak": 4.00,
            "Acoustic_Energy": 4.41,
            "Acoustic_Kurtosis": 9.5,
            "Acoustic_Skewness": 2.4,
            "Sensor_Anomaly_Score": 0.88,
            "Asset_Risk_Score": 0.95,
            "Water_Demand": 380.0,
            "Tank_Level": 2.1
        }
    },
    "vibration_anomaly": {
        "title": "Severe Vibration / Acoustic Anomaly",
        "description": "Service line exhibiting severe acoustic emissions and structural vibration spikes indicative of active stress.",
        "data": {
            "Asset_Type": "SERVICE",
            "Pipe_Material": "PVC",
            "Pipe_Diameter_cm": 10.0,
            "Pipe_Length_m": 45.0,
            "Pipe_Depth_m": 1.2,
            "Frost_Depth_m": 0.6,
            "Pipe_Age_Years": 22.0,
            "Condition_Score": 4.5,
            "Criticality": "High",
            "Criticality_Score": 7.0,
            "Lined": 0,
            "Undersized": 0,
            "Shallow_Main": 0,
            "Oversized": 0,
            "Cleaned": 0,
            "Pressure": 6.8,
            "Flow_Rate": 20.0,
            "Pressure_Deviation": 1.5,
            "Flow_Deviation": 1.8,
            "Pressure_Change_Rate": 0.45,
            "Flow_Change_Rate": 0.55,
            "Pressure_Flow_Ratio": 0.34,
            "Temperature_C": 28.0,
            "Year": 2026,
            "Month": 7,
            "Day": 20,
            "Hour": 17,
            "Day_of_Week": "Monday",
            "Season": "Summer",
            "Previous_Failures": 2,
            "Failures_Last_1_Year": 1,
            "Failures_Last_3_Years": 2,
            "Days_Since_Last_Failure": 110.0,
            "Days_Since_Last_Failure_Was_Missing": 0,
            "Vibration_RMS": 2.40,
            "Vibration_STD": 0.90,
            "Vibration_Min": 0.30,
            "Vibration_Max": 5.20,
            "Vibration_PeakToPeak": 4.90,
            "Vibration_Energy": 5.76,
            "Vibration_Kurtosis": 11.0,
            "Vibration_Skewness": 3.0,
            "Acoustic_RMS": 2.80,
            "Acoustic_STD": 1.10,
            "Acoustic_Min": 0.40,
            "Acoustic_Max": 6.00,
            "Acoustic_PeakToPeak": 5.60,
            "Acoustic_Energy": 7.84,
            "Acoustic_Kurtosis": 12.5,
            "Acoustic_Skewness": 3.4,
            "Sensor_Anomaly_Score": 0.94,
            "Asset_Risk_Score": 0.89,
            "Water_Demand": 220.0,
            "Tank_Level": 5.0
        }
    }
}

app = FastAPI(
    title="PowerGuard XGBoost Predictive Maintenance API",
    description="Production-grade API for pipe failure prediction using XGBoost and scikit-learn preprocessor pipeline.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionRequest(BaseModel):
    features: Dict[str, Any] = Field(
        ..., 
        description="Dictionary containing all 54 required features specified in input_schema.json"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "features": PRESETS["normal"]["data"]
            }
        }


@app.get("/api/health")
def health_check():
    """Health check endpoint to verify model and preprocessor status."""
    return {
        "status": "online",
        "service": "PowerGuard Predictive Maintenance API",
        "model": "XGBClassifier (xgboost_model.pkl)",
        "preprocessor": "ColumnTransformer (preprocessor.pkl)",
        "input_features": len(ALL_FEATURES),
        "threshold": THRESHOLD,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }


@app.get("/api/schema")
def get_schema():
    """Return schema, feature categories, categorical options, feature groups, and presets."""
    return {
        "number_of_features": len(ALL_FEATURES),
        "features": ALL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "categorical_values": CATEGORICAL_VALUES,
        "threshold": THRESHOLD,
        "feature_groups": FEATURE_GROUPS,
        "presets": PRESETS
    }


@app.post("/api/predict")
def predict(payload: PredictionRequest):
    """
    Accepts 54 raw input features, transforms them via preprocessor.pkl into 71 features,
    and returns XGBoost prediction probability, threshold comparison, and risk level.
    """
    input_dict = payload.features
    
    # 1. Check for missing features and populate defaults if necessary
    missing_features = []
    processed_dict = {}

    for feat in ALL_FEATURES:
        if feat not in input_dict:
            missing_features.append(feat)
            # Default fallback
            if feat in CATEGORICAL_FEATURES:
                processed_dict[feat] = CATEGORICAL_VALUES[feat][0]
            else:
                processed_dict[feat] = 0.0
        else:
            val = input_dict[feat]
            # Ensure correct categorical or numeric type
            if feat in CATEGORICAL_FEATURES:
                val_str = str(val).strip()
                allowed = CATEGORICAL_VALUES[feat]
                if val_str not in allowed:
                    # Fallback to closest or first allowed option if invalid string provided
                    logger.warning(f"Invalid categorical value '{val}' for '{feat}'. Allowed: {allowed}. Using '{allowed[0]}'.")
                    val_str = allowed[0]
                processed_dict[feat] = val_str
            else:
                try:
                    processed_dict[feat] = float(val)
                except (ValueError, TypeError):
                    raise HTTPException(
                        status_code=422, 
                        detail=f"Invalid numeric value '{val}' for feature '{feat}'. Must be a valid number."
                    )

    if missing_features:
        logger.info(f"Request missing {len(missing_features)} features. Filled with defaults: {missing_features}")

    # 2. Construct 1-row DataFrame maintaining exact feature order from ALL_FEATURES
    df_input = pd.DataFrame([processed_dict])[ALL_FEATURES]

    try:
        # 3. Transform via preprocessor (54 features -> 71 features)
        X_transformed = preprocessor.transform(df_input)
        
        # Verify shape (1, 71)
        n_rows, n_cols = X_transformed.shape
        if n_cols != 71:
            logger.warning(f"Expected 71 transformed features, got {n_cols}")

        # 4. Predict probabilities using XGBoost
        probabilities = xgboost_model.predict_proba(X_transformed)
        failure_prob = float(probabilities[0][1])  # Class 1 failure probability
        
        # 5. Evaluate against 0.65 decision threshold
        is_failure = bool(failure_prob >= THRESHOLD)

        # 6. Determine Risk Level
        if failure_prob >= THRESHOLD:
            risk_level = "High"
        elif failure_prob >= 0.30:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # Key analytical indicators for response card
        indicators = {
            "pipe_age": processed_dict.get("Pipe_Age_Years", 0.0),
            "condition_score": processed_dict.get("Condition_Score", 0.0),
            "pressure": processed_dict.get("Pressure", 0.0),
            "pressure_deviation": processed_dict.get("Pressure_Deviation", 0.0),
            "vibration_rms": processed_dict.get("Vibration_RMS", 0.0),
            "acoustic_rms": processed_dict.get("Acoustic_RMS", 0.0),
            "sensor_anomaly_score": processed_dict.get("Sensor_Anomaly_Score", 0.0),
            "asset_risk_score": processed_dict.get("Asset_Risk_Score", 0.0)
        }

        return {
            "success": True,
            "failure_probability": round(failure_prob, 4),
            "failure_probability_percentage": f"{round(failure_prob * 100, 2)}%",
            "threshold": THRESHOLD,
            "prediction": is_failure,
            "status": "Failure Expected" if is_failure else "Normal Operation",
            "risk_level": risk_level,
            "transformed_feature_count": n_cols,
            "key_indicators": indicators,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Error during prediction pipeline execution: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Inference pipeline execution error: {str(e)}"
        )


# Serve Static Web UI Files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    def read_root():
        index_file = STATIC_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "PowerGuard API is running. Static index.html not found in static/ directory."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
