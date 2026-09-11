"""
Aquora Decision System / Expert Logic Subsystem Router
Acts as an operational decision layer on top of the XGBoost failure prediction model.
Uses ONLY the remaining decision system artifacts.
"""

from pathlib import Path
from typing import Dict, Any, List
import json
import logging
import warnings

import backend.sklearn_compat
import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.expert_rules import evaluate_expert_decision

logger = logging.getLogger("aquora.decision")

router = APIRouter(prefix="/api/decision", tags=["Decision System"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# File paths
MODEL_PATH = BASE_DIR / "xgboost_model.pkl"
PREPROCESSOR_PATH = BASE_DIR / "preprocessor.pkl"
SCHEMA_PATH = BASE_DIR / "input_schema.json"
THRESHOLDS_PATH = BASE_DIR / "thresholds.json"
CONFIG_PATH = BASE_DIR / "decision_system_config.json"

# Load schema
if not SCHEMA_PATH.exists():
    raise FileNotFoundError(f"Input schema file not found: {SCHEMA_PATH}")

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    SCHEMA = json.load(f)

ALL_FEATURES: List[str] = SCHEMA["features"]
NUMERIC_FEATURES: List[str] = SCHEMA["numeric_features"]
CATEGORICAL_FEATURES: List[str] = SCHEMA["categorical_features"]
CATEGORICAL_VALUES: Dict[str, List[str]] = SCHEMA["categorical_values"]

# Decision threshold for XGBoost (0.65)
ML_THRESHOLD = 0.65
if THRESHOLDS_PATH.exists():
    with open(THRESHOLDS_PATH, "r", encoding="utf-8") as f:
        t_data = json.load(f)
        ML_THRESHOLD = float(t_data.get("XGBoost", 0.65))

# Expert System Configuration
CONFIG = {}
if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)

# Load Preprocessor and Model
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        decision_preprocessor = joblib.load(PREPROCESSOR_PATH)
        decision_model = joblib.load(MODEL_PATH)
    logger.info("Loaded Decision System XGBoost model and preprocessor successfully.")
except Exception as e:
    logger.error(f"Error loading decision system artifacts: {e}")
    decision_preprocessor = None
    decision_model = None

# Comprehensive Presets illustrating all 4 Expert Status Levels
PRESETS = {
    "normal_operational": {
        "title": "Level 1: Normal Asset (Score < 4)",
        "description": "Sound newly inspected pipeline operating well within design envelope; baseline score 1.",
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
            "Flow_Deviation": 0.10,
            "Pressure_Change_Rate": 0.01,
            "Flow_Change_Rate": 0.02,
            "Pressure_Flow_Ratio": 0.0933,
            "Temperature_C": 18.5,
            "Year": 2026,
            "Month": 9,
            "Day": 9,
            "Hour": 14,
            "Day_of_Week": "Wednesday",
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
    "warning_condition": {
        "title": "Level 2: Warning Condition (Score 4 - 11)",
        "description": "Aging main with moderate acoustic hum and pressure fluctuation; requires inspection within 14 days.",
        "data": {
            "Asset_Type": "MAIN",
            "Pipe_Material": "DI",
            "Pipe_Diameter_cm": 25.0,
            "Pipe_Length_m": 180.0,
            "Pipe_Depth_m": 1.5,
            "Frost_Depth_m": 0.8,
            "Pipe_Age_Years": 38.0,
            "Condition_Score": 4.2,
            "Criticality": "Medium",
            "Criticality_Score": 5.0,
            "Lined": 1,
            "Undersized": 0,
            "Shallow_Main": 0,
            "Oversized": 0,
            "Cleaned": 1,
            "Pressure": 4.8,
            "Flow_Rate": 36.0,
            "Pressure_Deviation": 1.20,
            "Flow_Deviation": 1.40,
            "Pressure_Change_Rate": 0.25,
            "Flow_Change_Rate": 0.30,
            "Pressure_Flow_Ratio": 0.133,
            "Temperature_C": 15.0,
            "Year": 2026,
            "Month": 9,
            "Day": 9,
            "Hour": 11,
            "Day_of_Week": "Wednesday",
            "Season": "Autumn",
            "Previous_Failures": 1,
            "Failures_Last_1_Year": 1,
            "Failures_Last_3_Years": 1,
            "Days_Since_Last_Failure": 180.0,
            "Days_Since_Last_Failure_Was_Missing": 0,
            "Vibration_RMS": 0.95,
            "Vibration_STD": 0.30,
            "Vibration_Min": 0.20,
            "Vibration_Max": 2.10,
            "Vibration_PeakToPeak": 1.90,
            "Vibration_Energy": 0.90,
            "Vibration_Kurtosis": 4.8,
            "Vibration_Skewness": 0.9,
            "Acoustic_RMS": 1.35,
            "Acoustic_STD": 0.40,
            "Acoustic_Min": 0.25,
            "Acoustic_Max": 2.80,
            "Acoustic_PeakToPeak": 2.55,
            "Acoustic_Energy": 1.82,
            "Acoustic_Kurtosis": 5.5,
            "Acoustic_Skewness": 1.2,
            "Sensor_Anomaly_Score": 0.55,
            "Asset_Risk_Score": 0.62,
            "Water_Demand": 190.0,
            "Tank_Level": 5.8
        }
    },
    "high_risk_degraded": {
        "title": "Level 3: High Risk Asset (Score 12 - 17)",
        "description": "Cast-iron main over 50 years old with past breaks and high ML failure probability.",
        "data": {
            "Asset_Type": "MAIN",
            "Pipe_Material": "CI",
            "Pipe_Diameter_cm": 15.0,
            "Pipe_Length_m": 250.0,
            "Pipe_Depth_m": 0.9,
            "Frost_Depth_m": 1.2,
            "Pipe_Age_Years": 55.0,
            "Condition_Score": 2.1,
            "Criticality": "High",
            "Criticality_Score": 8.0,
            "Lined": 0,
            "Undersized": 1,
            "Shallow_Main": 1,
            "Oversized": 0,
            "Cleaned": 0,
            "Pressure": 7.5,
            "Flow_Rate": 16.0,
            "Pressure_Deviation": 2.2,
            "Flow_Deviation": 2.8,
            "Pressure_Change_Rate": 0.65,
            "Flow_Change_Rate": 0.70,
            "Pressure_Flow_Ratio": 0.468,
            "Temperature_C": 2.0,
            "Year": 2026,
            "Month": 1,
            "Day": 15,
            "Hour": 3,
            "Day_of_Week": "Thursday",
            "Season": "Winter",
            "Previous_Failures": 4,
            "Failures_Last_1_Year": 1,
            "Failures_Last_3_Years": 3,
            "Days_Since_Last_Failure": 75.0,
            "Days_Since_Last_Failure_Was_Missing": 0,
            "Vibration_RMS": 1.85,
            "Vibration_STD": 0.65,
            "Vibration_Min": 0.40,
            "Vibration_Max": 3.90,
            "Vibration_PeakToPeak": 3.50,
            "Vibration_Energy": 3.42,
            "Vibration_Kurtosis": 8.2,
            "Vibration_Skewness": 2.1,
            "Acoustic_RMS": 1.95,
            "Acoustic_STD": 0.70,
            "Acoustic_Min": 0.45,
            "Acoustic_Max": 4.10,
            "Acoustic_PeakToPeak": 3.65,
            "Acoustic_Energy": 3.80,
            "Acoustic_Kurtosis": 8.8,
            "Acoustic_Skewness": 2.2,
            "Sensor_Anomaly_Score": 0.84,
            "Asset_Risk_Score": 0.88,
            "Water_Demand": 320.0,
            "Tank_Level": 3.4
        }
    },
    "critical_emergency": {
        "title": "Level 4: Critical Emergency State (Score >= 18)",
        "description": "Extreme structural distress, severe pressure surge, acoustic burst spikes, and 90%+ failure risk.",
        "data": {
            "Asset_Type": "MAIN",
            "Pipe_Material": "CI",
            "Pipe_Diameter_cm": 20.0,
            "Pipe_Length_m": 300.0,
            "Pipe_Depth_m": 0.8,
            "Frost_Depth_m": 1.4,
            "Pipe_Age_Years": 62.0,
            "Condition_Score": 1.4,
            "Criticality": "Critical",
            "Criticality_Score": 9.8,
            "Lined": 0,
            "Undersized": 1,
            "Shallow_Main": 1,
            "Oversized": 0,
            "Cleaned": 0,
            "Pressure": 9.2,
            "Flow_Rate": 8.0,
            "Pressure_Deviation": 3.4,
            "Flow_Deviation": 4.2,
            "Pressure_Change_Rate": 0.95,
            "Flow_Change_Rate": 0.98,
            "Pressure_Flow_Ratio": 1.15,
            "Temperature_C": -4.0,
            "Year": 2026,
            "Month": 1,
            "Day": 18,
            "Hour": 2,
            "Day_of_Week": "Sunday",
            "Season": "Winter",
            "Previous_Failures": 6,
            "Failures_Last_1_Year": 2,
            "Failures_Last_3_Years": 5,
            "Days_Since_Last_Failure": 28.0,
            "Days_Since_Last_Failure_Was_Missing": 0,
            "Vibration_RMS": 2.65,
            "Vibration_STD": 0.95,
            "Vibration_Min": 0.50,
            "Vibration_Max": 5.80,
            "Vibration_PeakToPeak": 5.30,
            "Vibration_Energy": 7.02,
            "Vibration_Kurtosis": 12.0,
            "Vibration_Skewness": 3.2,
            "Acoustic_RMS": 3.10,
            "Acoustic_STD": 1.15,
            "Acoustic_Min": 0.60,
            "Acoustic_Max": 6.50,
            "Acoustic_PeakToPeak": 5.90,
            "Acoustic_Energy": 9.61,
            "Acoustic_Kurtosis": 13.5,
            "Acoustic_Skewness": 3.8,
            "Sensor_Anomaly_Score": 0.96,
            "Asset_Risk_Score": 0.98,
            "Water_Demand": 410.0,
            "Tank_Level": 1.8
        }
    }
}

class DecisionPredictionRequest(BaseModel):
    features: Dict[str, Any] = Field(
        ...,
        description="Dictionary of 54 raw features matching input_schema.json"
    )

@router.get("/schema")
def get_decision_schema():
    """Return schema, feature categories, and curated presets."""
    return {
        "number_of_features": len(ALL_FEATURES),
        "features": ALL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "categorical_values": CATEGORICAL_VALUES,
        "ml_threshold": ML_THRESHOLD,
        "presets": PRESETS
    }

@router.get("/config")
def get_decision_config():
    """Return expert score levels and output configuration."""
    return CONFIG

@router.post("/predict")
def predict_decision(payload: DecisionPredictionRequest):
    """
    Executes the two-stage decision pipeline:
    1. ML Model: Preprocessor (54 -> 71 features) + XGBoost -> Failure Probability & ML Threshold check.
    2. Expert Rule Layer: Evaluates heuristics, telemetry, and ML score to determine Expert Score,
       Final Status, Triggered Reasons, and Recommended Operational Action.
    """
    if decision_preprocessor is None or decision_model is None:
        raise HTTPException(status_code=503, detail="Decision System models not loaded.")

    input_dict = payload.features

    processed_dict = {}
    for feat in ALL_FEATURES:
        if feat not in input_dict:
            if feat in CATEGORICAL_FEATURES:
                processed_dict[feat] = CATEGORICAL_VALUES[feat][0]
            else:
                processed_dict[feat] = 0.0
        else:
            val = input_dict[feat]
            if feat in CATEGORICAL_FEATURES:
                val_str = str(val).strip()
                if val_str not in CATEGORICAL_VALUES[feat]:
                    val_str = CATEGORICAL_VALUES[feat][0]
                processed_dict[feat] = val_str
            else:
                try:
                    processed_dict[feat] = float(val)
                except (ValueError, TypeError):
                    processed_dict[feat] = 0.0

    df_input = pd.DataFrame([processed_dict])[ALL_FEATURES]

    try:
        # Step 1: ML Model Transformation & Inference
        X_trans = decision_preprocessor.transform(df_input)
        probabilities = decision_model.predict_proba(X_trans)
        failure_prob = float(probabilities[0][1])
        is_ml_failure = bool(failure_prob >= ML_THRESHOLD)

        if failure_prob >= ML_THRESHOLD:
            ml_risk_level = "High"
        elif failure_prob >= 0.30:
            ml_risk_level = "Medium"
        else:
            ml_risk_level = "Low"

        # Step 2: Expert Rule Layer Evaluation
        expert_result = evaluate_expert_decision(
            raw_features=processed_dict,
            failure_probability=failure_prob,
            ml_threshold=ML_THRESHOLD
        )

        return {
            "success": True,
            # AI ML Model Output
            "ai_prediction": {
                "failure_probability": round(failure_prob, 4),
                "failure_probability_percentage": f"{round(failure_prob * 100, 2)}%",
                "ml_threshold": ML_THRESHOLD,
                "ml_prediction": is_ml_failure,
                "ml_status": "Failure Expected" if is_ml_failure else "Normal Operation",
                "ml_risk_level": ml_risk_level,
                "target": "Failure_Next_30_Days"
            },
            # Expert System Decision Layer Output
            "expert_decision": {
                "expert_score": expert_result["expert_score"],
                "final_status": expert_result["final_status"],
                "score_levels": {
                    "NORMAL": "< 4",
                    "WARNING": "4-11",
                    "HIGH RISK": "12-17",
                    "CRITICAL": ">= 18"
                },
                "reasons": expert_result["reasons"],
                "recommended_action": expert_result["recommended_action"],
                "contributing_factors": expert_result["contributing_factors"]
            },
            # Key Indicators for display
            "key_indicators": {
                "Pipe_Age_Years": processed_dict.get("Pipe_Age_Years", 0.0),
                "Condition_Score": processed_dict.get("Condition_Score", 0.0),
                "Pressure": processed_dict.get("Pressure", 0.0),
                "Pressure_Deviation": processed_dict.get("Pressure_Deviation", 0.0),
                "Vibration_RMS": processed_dict.get("Vibration_RMS", 0.0),
                "Acoustic_RMS": processed_dict.get("Acoustic_RMS", 0.0),
                "Sensor_Anomaly_Score": processed_dict.get("Sensor_Anomaly_Score", 0.0),
                "Asset_Risk_Score": processed_dict.get("Asset_Risk_Score", 0.0)
            }
        }

    except Exception as e:
        logger.error(f"Decision system execution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Decision system inference failed: {str(e)}")
