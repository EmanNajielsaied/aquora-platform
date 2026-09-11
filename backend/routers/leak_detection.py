"""
Aquora Leak Detection Subsystem Router
Isolated inference endpoint for the XGBoost leak detection model and preprocessing pipeline.
Uses ONLY detect_* files.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import logging
import warnings

import backend.sklearn_compat
import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.expert_rules import evaluate_expert_decision

logger = logging.getLogger("aquora.leak")

router = APIRouter(prefix="/api/leak", tags=["Leak Detection"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent

import xgboost as xgb

# File paths strictly using detect_* artifacts
MODEL_PKL_PATH = BASE_DIR / "detect_xgboost_model (1).pkl"
MODEL_UBJ_PATH = BASE_DIR / "detect_xgboost_model.ubj"
PREPROCESSOR_PATH = BASE_DIR / "detect_preprocessor (3).pkl"
FEATURE_INFO_PATH = BASE_DIR / "detect_feature_info (1).json"
THRESHOLD_PATH = BASE_DIR / "detect_threshold.json"
METRICS_PATH = BASE_DIR / "detect_xgboost_metrics.json"

# Load metadata
if not FEATURE_INFO_PATH.exists():
    raise FileNotFoundError(f"Feature info file not found: {FEATURE_INFO_PATH}")

with open(FEATURE_INFO_PATH, "r", encoding="utf-8") as f:
    FEATURE_INFO = json.load(f)

RAW_FEATURES: List[str] = FEATURE_INFO["raw_input_features"]
NUMERICAL_FEATURES: List[str] = FEATURE_INFO["numerical_features"]
CATEGORICAL_FEATURES: List[str] = FEATURE_INFO["categorical_features"]

# Load exact threshold from detect_threshold.json
DEFAULT_THRESHOLD = 0.38803765177726746
if THRESHOLD_PATH.exists():
    with open(THRESHOLD_PATH, "r", encoding="utf-8") as f:
        t_data = json.load(f)
        THRESHOLD = float(t_data.get("threshold", DEFAULT_THRESHOLD))
else:
    THRESHOLD = DEFAULT_THRESHOLD

# Load evaluation metrics
METRICS = {}
if METRICS_PATH.exists():
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        METRICS = json.load(f)

# Load preprocessor and model
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        leak_preprocessor = joblib.load(PREPROCESSOR_PATH)
        if MODEL_UBJ_PATH.exists():
            leak_model = xgb.XGBClassifier()
            leak_model.load_model(str(MODEL_UBJ_PATH))
        else:
            leak_model = joblib.load(MODEL_PKL_PATH)
    logger.info("Loaded Leak Detection preprocessor and XGBoost model successfully.")
except Exception as e:
    logger.error(f"Error loading leak detection artifacts: {e}")
    leak_preprocessor = None
    leak_model = None

# Curated Presets for demonstration
PRESETS = {
    "intact_normal": {
        "title": "Intact Main Pipe (Normal Operation)",
        "description": "Sound main pipe operating under balanced hydraulic pressure with baseline acoustic silence.",
        "data": {
            "Asset_Type": "MAIN",
            "Pipe_Material": "DI",
            "Pipe_Diameter_cm": 68.0,
            "Pipe_Length_m": 80.0,
            "Pipe_Depth_m": 1.35,
            "Frost_Depth_m": 0.76,
            "Installation_Year": 2018,
            "Pipe_Age_Years": 8.0,
            "Condition_Score": 75.0,
            "Criticality": "Medium",
            "Criticality_Score": 0.52,
            "Lined": 1,
            "Undersized": 0,
            "Shallow_Main": 0,
            "Oversized": 0,
            "Cleaned": 1,
            "Pressure": 466.7,
            "Flow_Rate": 24.5,
            "Pressure_Deviation": 0.0,
            "Flow_Deviation": 0.0,
            "Pressure_Change_Rate": 0.0,
            "Flow_Change_Rate": 0.0,
            "Pressure_Flow_Ratio": 20.7,
            "Temperature_C": 18.5,
            "pH": 7.2,
            "TDS_mg_L": 220.0,
            "Turbidity_NTU": 1.2,
            "Dissolved_Oxygen_mg_L": 8.5,
            "Conductivity_umhos_cm": 350.0,
            "BOD_mg_L": 2.36,
            "Nitrate_Nitrite_mg_L": 2.0,
            "Fecal_Coliform_MPN_100ml": 0.0,
            "Total_Coliform_MPN_100ml": 0.0,
            "Year": 2026,
            "Month": 9,
            "Day": 9,
            "Hour": 14,
            "Day_of_Week": "Wednesday",
            "Season": "Autumn",
            "Previous_Failures": 0,
            "Failures_Last_1_Year": 0,
            "Failures_Last_3_Years": 0,
            "Failures_Last_5_Years": 0,
            "Days_Since_Last_Failure": 1825.0,
            "Vibration_RMS": 0.94,
            "Vibration_STD": 0.36,
            "Vibration_Min": 0.59,
            "Vibration_Max": 1.50,
            "Vibration_PeakToPeak": 0.90,
            "Vibration_Energy": 1.00,
            "Vibration_Kurtosis": 3.13,
            "Vibration_Skewness": 0.10,
            "Acoustic_RMS": 0.67,
            "Acoustic_STD": 0.28,
            "Acoustic_Min": 0.43,
            "Acoustic_Max": 1.12,
            "Acoustic_PeakToPeak": 0.69,
            "Acoustic_Energy": 0.56,
            "Acoustic_Kurtosis": 3.17,
            "Acoustic_Skewness": 0.09,
            "Sensor_Anomaly_Score": 0.15,
            "Water_Quality_Index": 88.5,
            "Asset_Risk_Score": 0.35,
            "Days_Since_Last_Failure_Was_Missing": 0,
            "Water_Demand": 150.0,
            "Tank_Level": 7.5
        }
    },
    "active_leak": {
        "title": "Active High-Pressure Pipe Leak (Detected)",
        "description": "Pipe orifice breach with 26.4 kPa pressure drop, +16.8 L/s flow deviation, soil water coliform ingress, and recurring failure history.",
        "data": {
            "Asset_Type": "MAIN",
            "Pipe_Material": "CI",
            "Pipe_Diameter_cm": 71.1,
            "Pipe_Length_m": 80.0,
            "Pipe_Depth_m": 1.38,
            "Frost_Depth_m": 1.02,
            "Installation_Year": 2018,
            "Pipe_Age_Years": 8.0,
            "Condition_Score": 95.4,
            "Criticality": "High",
            "Criticality_Score": 0.88,
            "Lined": 1,
            "Undersized": 0,
            "Shallow_Main": 0,
            "Oversized": 1,
            "Cleaned": 1,
            "Pressure": 402.5,
            "Flow_Rate": 22.3,
            "Pressure_Deviation": -26.42,
            "Flow_Deviation": 16.77,
            "Pressure_Change_Rate": -6.99,
            "Flow_Change_Rate": -19.7,
            "Pressure_Flow_Ratio": 22.53,
            "Temperature_C": 8.65,
            "pH": 8.05,
            "TDS_mg_L": 222.0,
            "Turbidity_NTU": 3.28,
            "Dissolved_Oxygen_mg_L": 10.64,
            "Conductivity_umhos_cm": 456.8,
            "BOD_mg_L": 2.55,
            "Nitrate_Nitrite_mg_L": 1.0,
            "Fecal_Coliform_MPN_100ml": 79.6,
            "Total_Coliform_MPN_100ml": 265.5,
            "Year": 2026,
            "Month": 12,
            "Day": 5,
            "Hour": 18,
            "Day_of_Week": "Monday",
            "Season": "Autumn",
            "Previous_Failures": 14,
            "Failures_Last_1_Year": 2,
            "Failures_Last_3_Years": 4,
            "Failures_Last_5_Years": 10,
            "Days_Since_Last_Failure": 55.0,
            "Vibration_RMS": 0.94,
            "Vibration_STD": 0.28,
            "Vibration_Min": 0.38,
            "Vibration_Max": 2.15,
            "Vibration_PeakToPeak": 0.90,
            "Vibration_Energy": 0.38,
            "Vibration_Kurtosis": 3.11,
            "Vibration_Skewness": -0.13,
            "Acoustic_RMS": 0.67,
            "Acoustic_STD": 0.24,
            "Acoustic_Min": 1.02,
            "Acoustic_Max": 1.02,
            "Acoustic_PeakToPeak": 0.99,
            "Acoustic_Energy": 1.68,
            "Acoustic_Kurtosis": 1.35,
            "Acoustic_Skewness": -0.21,
            "Sensor_Anomaly_Score": 0.14,
            "Water_Quality_Index": 96.2,
            "Asset_Risk_Score": 0.19,
            "Days_Since_Last_Failure_Was_Missing": 0,
            "Water_Demand": 20.7,
            "Tank_Level": 3.4
        }
    },
    "micro_leak_warning": {
        "title": "Early Stage Micro-Leak / Joint Stress",
        "description": "Moderate acoustic hiss and pressure fluctuation indicative of developing joint loosening.",
        "data": {
            "Asset_Type": "MAIN",
            "Pipe_Material": "CI",
            "Pipe_Diameter_cm": 50.0,
            "Pipe_Length_m": 90.0,
            "Pipe_Depth_m": 1.3,
            "Frost_Depth_m": 0.7,
            "Installation_Year": 1995,
            "Pipe_Age_Years": 31.0,
            "Condition_Score": 48.0,
            "Criticality": "Medium",
            "Criticality_Score": 0.55,
            "Lined": 1,
            "Undersized": 0,
            "Shallow_Main": 0,
            "Oversized": 0,
            "Cleaned": 1,
            "Pressure": 445.0,
            "Flow_Rate": 20.0,
            "Pressure_Deviation": -25.0,
            "Flow_Deviation": -12.0,
            "Pressure_Change_Rate": 5.0,
            "Flow_Change_Rate": 6.0,
            "Pressure_Flow_Ratio": 22.2,
            "Temperature_C": 16.0,
            "pH": 7.1,
            "TDS_mg_L": 260.0,
            "Turbidity_NTU": 2.8,
            "Dissolved_Oxygen_mg_L": 7.5,
            "Conductivity_umhos_cm": 370.0,
            "BOD_mg_L": 2.8,
            "Nitrate_Nitrite_mg_L": 2.5,
            "Fecal_Coliform_MPN_100ml": 0.0,
            "Total_Coliform_MPN_100ml": 1.0,
            "Year": 2026,
            "Month": 9,
            "Day": 9,
            "Hour": 10,
            "Day_of_Week": "Wednesday",
            "Season": "Autumn",
            "Previous_Failures": 1,
            "Failures_Last_1_Year": 0,
            "Failures_Last_3_Years": 1,
            "Failures_Last_5_Years": 1,
            "Days_Since_Last_Failure": 380.0,
            "Vibration_RMS": 1.25,
            "Vibration_STD": 0.45,
            "Vibration_Min": 0.50,
            "Vibration_Max": 2.10,
            "Vibration_PeakToPeak": 1.60,
            "Vibration_Energy": 1.56,
            "Vibration_Kurtosis": 4.2,
            "Vibration_Skewness": 0.6,
            "Acoustic_RMS": 1.15,
            "Acoustic_STD": 0.42,
            "Acoustic_Min": 0.38,
            "Acoustic_Max": 1.95,
            "Acoustic_PeakToPeak": 1.57,
            "Acoustic_Energy": 1.32,
            "Acoustic_Kurtosis": 4.5,
            "Acoustic_Skewness": 0.8,
            "Sensor_Anomaly_Score": 0.62,
            "Water_Quality_Index": 82.0,
            "Asset_Risk_Score": 0.65,
            "Days_Since_Last_Failure_Was_Missing": 0,
            "Water_Demand": 180.0,
            "Tank_Level": 5.9
        }
    }
}

class LeakPredictionRequest(BaseModel):
    features: Dict[str, Any] = Field(
        ...,
        description="Dictionary containing raw input features matching detect_feature_info.json"
    )

@router.get("/schema")
def get_leak_schema():
    """Return raw feature names, categorical sets, decision threshold, and presets."""
    return {
        "raw_input_feature_count": len(RAW_FEATURES),
        "raw_input_features": RAW_FEATURES,
        "numerical_features": NUMERICAL_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "decision_threshold": THRESHOLD,
        "threshold_selection": "maximum F1 on validation set",
        "target": "Leak_No_Leak",
        "presets": PRESETS
    }

@router.get("/metrics")
def get_leak_metrics():
    """Return model performance metrics from detect_xgboost_metrics.json."""
    return {
        "model": "XGBoost Classifier (detect_xgboost_model)",
        "threshold": THRESHOLD,
        "metrics": METRICS
    }

@router.post("/predict")
def predict_leak(payload: LeakPredictionRequest):
    """
    Accepts raw features for leak detection, transforms via detect_preprocessor (66 -> 82 features),
    predicts leak probability with XGBoost, and compares against the saved 0.3880 threshold.
    """
    if leak_preprocessor is None or leak_model is None:
        raise HTTPException(status_code=503, detail="Leak Detection models not loaded.")

    input_dict = payload.features

    # Populate defaults while preserving strict feature ordering
    processed_dict = {}
    default_cat_map = {
        "Asset_Type": "MAIN",
        "Pipe_Material": "DI",
        "Criticality": "Medium",
        "Day_of_Week": "Monday",
        "Season": "Autumn"
    }

    for feat in RAW_FEATURES:
        if feat in input_dict:
            val = input_dict[feat]
            if feat in CATEGORICAL_FEATURES:
                processed_dict[feat] = str(val).strip()
            else:
                try:
                    processed_dict[feat] = float(val)
                except (ValueError, TypeError):
                    processed_dict[feat] = 0.0
        else:
            if feat in CATEGORICAL_FEATURES:
                processed_dict[feat] = default_cat_map.get(feat, "Unknown")
            else:
                processed_dict[feat] = 0.0

    # Construct single-row DataFrame maintaining exact column order
    df_input = pd.DataFrame([processed_dict])[RAW_FEATURES]

    try:
        # Transform via detect_preprocessor (66 raw -> 82 features)
        X_trans = leak_preprocessor.transform(df_input)

        # Predict probability
        probs = leak_model.predict_proba(X_trans)
        leak_prob = float(probs[0][1])  # Class 1 is Leak

        # Threshold comparison strictly using saved threshold
        is_leak = bool(leak_prob >= THRESHOLD)

        # Risk Level determination
        if leak_prob >= THRESHOLD:
            risk_level = "High"
        elif leak_prob >= 0.20:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # Extract Key Indicators
        key_indicators = {
            "Pipe_Age_Years": processed_dict.get("Pipe_Age_Years", 0.0),
            "Condition_Score": processed_dict.get("Condition_Score", 0.0),
            "Pressure": processed_dict.get("Pressure", 0.0),
            "Pressure_Deviation": processed_dict.get("Pressure_Deviation", 0.0),
            "Vibration_RMS": processed_dict.get("Vibration_RMS", 0.0),
            "Acoustic_RMS": processed_dict.get("Acoustic_RMS", 0.0),
            "Sensor_Anomaly_Score": processed_dict.get("Sensor_Anomaly_Score", 0.0),
            "Asset_Risk_Score": processed_dict.get("Asset_Risk_Score", 0.0)
        }

        # Integrated Supporting Expert System Analysis
        expert_result = evaluate_expert_decision(
            raw_features=processed_dict,
            failure_probability=leak_prob,
            ml_threshold=THRESHOLD
        )

        return {
            "success": True,
            # Primary AI / ML Leak Prediction
            "ai_prediction": {
                "leak_probability": round(leak_prob, 4),
                "leak_probability_percentage": f"{round(leak_prob * 100, 2)}%",
                "decision_threshold": THRESHOLD,
                "decision_threshold_formatted": f"{THRESHOLD:.4f}",
                "decision_threshold_percentage": f"{round(THRESHOLD * 100, 2)}%",
                "prediction": is_leak,
                "status": "Leak Detected" if is_leak else "No Leak Detected",
                "risk_level": risk_level,
                "target": "Leak_No_Leak"
            },
            # Backward compatibility fields
            "leak_probability": round(leak_prob, 4),
            "leak_probability_percentage": f"{round(leak_prob * 100, 2)}%",
            "decision_threshold": THRESHOLD,
            "decision_threshold_formatted": f"{THRESHOLD:.4f}",
            "prediction": is_leak,
            "status": "Leak Detected" if is_leak else "No Leak Detected",
            "risk_level": risk_level,
            # Key Analytical Indicators
            "key_indicators": key_indicators,
            # Supporting Expert System Analysis
            "expert_analysis": {
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
            }
        }

    except Exception as e:
        logger.error(f"Leak detection prediction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Leak detection inference failed: {str(e)}")
