"""
Aquora Decision System - Expert Rule Evaluation Engine
Implements domain-expert heuristics and decision logic on top of the
XGBoost predictive maintenance ML model according to decision_system_config.json.
"""

from typing import Dict, Any, List, Tuple

# Level boundaries from decision_system_config.json
SCORE_LEVELS = {
    "NORMAL": lambda score: score < 4,
    "WARNING": lambda score: 4 <= score <= 11,
    "HIGH RISK": lambda score: 12 <= score <= 17,
    "CRITICAL": lambda score: score >= 18,
}

RECOMMENDED_ACTIONS = {
    "NORMAL": (
        "Asset operating within baseline hydraulic and structural tolerances. "
        "Maintain standard quarterly SCADA logging and planned preventative maintenance cycles."
    ),
    "WARNING": (
        "Elevated telemetry drift or early degradation detected. "
        "Increase sensor sampling frequency to bi-hourly, inspect local pressure relief valves, "
        "and schedule non-destructive acoustic survey within 14 days."
    ),
    "HIGH RISK": (
        "Significant structural fatigue, severe vibration/acoustic spikes, or high ML failure risk. "
        "Dispatch field engineering crew for physical site inspection within 48 hours. "
        "Restrict localized line pressure to prevent rapid burst progression."
    ),
    "CRITICAL": (
        "IMMEDIATE ACTION REQUIRED: Asset in critical imminent failure state. "
        "Execute automated emergency sectional isolation protocols, reroute flow through redundant "
        "distribution loops, notify municipal response command, and mobilize emergency repair crews immediately."
    )
}

def evaluate_expert_decision(
    raw_features: Dict[str, Any],
    failure_probability: float,
    ml_threshold: float = 0.65
) -> Dict[str, Any]:
    """
    Evaluates rule triggers across asset condition, telemetry spikes, historical breaks,
    and machine learning probability to compute an expert score and determine final operational status.
    """
    score = 0
    reasons: List[str] = []
    contributing_factors: List[Dict[str, Any]] = []

    # 1. Machine Learning Prediction Contribution
    is_ml_failure = failure_probability >= ml_threshold
    if is_ml_failure:
        ml_pts = 6 if failure_probability >= 0.85 else 5
        score += ml_pts
        reasons.append(
            f"ML Predictive Model indicates failure risk ({failure_probability:.1%} >= {ml_threshold:.0%} threshold) (+{ml_pts} pts)"
        )
        contributing_factors.append({
            "category": "AI Prediction",
            "feature": "Failure_Probability",
            "value": f"{failure_probability:.1%}",
            "points": ml_pts
        })
    elif failure_probability >= 0.35:
        score += 2
        reasons.append(
            f"ML Predictive Model indicates moderate failure tendency ({failure_probability:.1%}) (+2 pts)"
        )
        contributing_factors.append({
            "category": "AI Prediction",
            "feature": "Failure_Probability",
            "value": f"{failure_probability:.1%}",
            "points": 2
        })

    # 2. Asset Physical Degradation & Pipe Age
    age = float(raw_features.get("Pipe_Age_Years", 0.0))
    condition = float(raw_features.get("Condition_Score", 10.0))
    material = str(raw_features.get("Pipe_Material", "")).upper()
    criticality = str(raw_features.get("Criticality", "")).capitalize()

    if age >= 50.0:
        score += 3
        reasons.append(f"Severe pipe aging: asset age is {age:.1f} years (>= 50 yrs) (+3 pts)")
        contributing_factors.append({"category": "Asset Health", "feature": "Pipe_Age_Years", "value": f"{age} yrs", "points": 3})
    elif age >= 35.0:
        score += 2
        reasons.append(f"Elevated pipe age: asset age is {age:.1f} years (>= 35 yrs) (+2 pts)")
        contributing_factors.append({"category": "Asset Health", "feature": "Pipe_Age_Years", "value": f"{age} yrs", "points": 2})

    if condition <= 2.5:
        score += 3
        reasons.append(f"Poor structural condition index: score is {condition:.1f}/10 (<= 2.5) (+3 pts)")
        contributing_factors.append({"category": "Asset Health", "feature": "Condition_Score", "value": f"{condition}/10", "points": 3})
    elif condition <= 4.5:
        score += 2
        reasons.append(f"Degraded structural condition: score is {condition:.1f}/10 (<= 4.5) (+2 pts)")
        contributing_factors.append({"category": "Asset Health", "feature": "Condition_Score", "value": f"{condition}/10", "points": 2})

    if material in ["CI", "CAST IRON"]:
        score += 1
        reasons.append("High-brittleness legacy pipe material (Cast Iron) (+1 pt)")
        contributing_factors.append({"category": "Asset Health", "feature": "Pipe_Material", "value": material, "points": 1})

    if criticality == "Critical":
        score += 2
        reasons.append("High municipal network criticality asset (Critical) (+2 pts)")
        contributing_factors.append({"category": "Asset Health", "feature": "Criticality", "value": "Critical", "points": 2})

    # 3. Acoustic & Vibration Sensor Telemetry
    vib_rms = float(raw_features.get("Vibration_RMS", 0.0))
    vib_kurt = float(raw_features.get("Vibration_Kurtosis", 3.0))
    acoust_rms = float(raw_features.get("Acoustic_RMS", 0.0))
    acoust_kurt = float(raw_features.get("Acoustic_Kurtosis", 3.0))

    if acoust_rms >= 2.0:
        score += 3
        reasons.append(f"Severe acoustic emission energy: {acoust_rms:.2f} (>= 2.0 RMS) indicates active pipe stress/leak (+3 pts)")
        contributing_factors.append({"category": "Acoustic Telemetry", "feature": "Acoustic_RMS", "value": f"{acoust_rms:.2f}", "points": 3})
    elif acoust_rms >= 1.0:
        score += 1
        reasons.append(f"Elevated acoustic emission reading: {acoust_rms:.2f} (>= 1.0 RMS) (+1 pt)")
        contributing_factors.append({"category": "Acoustic Telemetry", "feature": "Acoustic_RMS", "value": f"{acoust_rms:.2f}", "points": 1})

    if acoust_kurt >= 8.0:
        score += 1
        reasons.append(f"Acoustic impulsive kurtosis spike: {acoust_kurt:.1f} indicates transient burst activity (+1 pt)")
        contributing_factors.append({"category": "Acoustic Telemetry", "feature": "Acoustic_Kurtosis", "value": f"{acoust_kurt:.1f}", "points": 1})

    if vib_rms >= 1.8:
        score += 3
        reasons.append(f"High structural vibration intensity: {vib_rms:.2f} (>= 1.8 RMS) indicates mechanical instability (+3 pts)")
        contributing_factors.append({"category": "Vibration Telemetry", "feature": "Vibration_RMS", "value": f"{vib_rms:.2f}", "points": 3})
    elif vib_rms >= 0.8:
        score += 1
        reasons.append(f"Elevated structural vibration: {vib_rms:.2f} (>= 0.8 RMS) (+1 pt)")
        contributing_factors.append({"category": "Vibration Telemetry", "feature": "Vibration_RMS", "value": f"{vib_rms:.2f}", "points": 1})

    # 4. Hydraulics & Pressure Deviation
    press_dev = abs(float(raw_features.get("Pressure_Deviation", 0.0)))
    if press_dev >= 2.0:
        score += 3
        reasons.append(f"Severe hydraulic surge/pressure deviation: {press_dev:.2f} bar (>= 2.0 bar) (+3 pts)")
        contributing_factors.append({"category": "Hydraulics", "feature": "Pressure_Deviation", "value": f"{press_dev:.2f} bar", "points": 3})
    elif press_dev >= 1.0:
        score += 1
        reasons.append(f"Moderate pressure variance: {press_dev:.2f} bar (>= 1.0 bar) (+1 pt)")
        contributing_factors.append({"category": "Hydraulics", "feature": "Pressure_Deviation", "value": f"{press_dev:.2f} bar", "points": 1})

    # 5. Incident & Historical Failures
    prev_failures = int(float(raw_features.get("Previous_Failures", 0)))
    failures_1yr = int(float(raw_features.get("Failures_Last_1_Year", 0)))
    days_since_failure = float(raw_features.get("Days_Since_Last_Failure", 9999.0))

    if failures_1yr >= 2:
        score += 3
        reasons.append(f"Recurrent failure frequency: {failures_1yr} break incidents in the past 12 months (+3 pts)")
        contributing_factors.append({"category": "Maintenance History", "feature": "Failures_Last_1_Year", "value": f"{failures_1yr} breaks", "points": 3})
    elif failures_1yr == 1:
        score += 1
        reasons.append("Recent break incident recorded within the past 12 months (+1 pt)")
        contributing_factors.append({"category": "Maintenance History", "feature": "Failures_Last_1_Year", "value": "1 break", "points": 1})

    if prev_failures >= 4:
        score += 2
        reasons.append(f"Chronic failure history: {prev_failures} cumulative lifetime breaks (+2 pts)")
        contributing_factors.append({"category": "Maintenance History", "feature": "Previous_Failures", "value": f"{prev_failures} breaks", "points": 2})

    if days_since_failure <= 90.0 and prev_failures > 0:
        score += 1
        reasons.append(f"Recent repair site: last break occurred {days_since_failure:.0f} days ago (<= 90 days) (+1 pt)")
        contributing_factors.append({"category": "Maintenance History", "feature": "Days_Since_Last_Failure", "value": f"{days_since_failure:.0f} days", "points": 1})

    # 6. Anomaly & Asset Risk Scores
    anomaly_score = float(raw_features.get("Sensor_Anomaly_Score", 0.0))
    risk_score = float(raw_features.get("Asset_Risk_Score", 0.0))

    if anomaly_score >= 0.8:
        score += 2
        reasons.append(f"Automated sensor anomaly index is high: {anomaly_score:.2f} (>= 0.80) (+2 pts)")
        contributing_factors.append({"category": "System Risk", "feature": "Sensor_Anomaly_Score", "value": f"{anomaly_score:.2f}", "points": 2})

    if risk_score >= 0.85:
        score += 2
        reasons.append(f"Composite asset vulnerability index is elevated: {risk_score:.2f} (>= 0.85) (+2 pts)")
        contributing_factors.append({"category": "System Risk", "feature": "Asset_Risk_Score", "value": f"{risk_score:.2f}", "points": 2})

    # If no rules triggered, provide baseline normal reason
    if not reasons:
        reasons.append("All structural, hydraulic, and acoustic parameters fall within normal operating bounds (0 pts).")

    # Map score to final status
    if score < 4:
        final_status = "NORMAL"
    elif 4 <= score <= 11:
        final_status = "WARNING"
    elif 12 <= score <= 17:
        final_status = "HIGH RISK"
    else:
        final_status = "CRITICAL"

    recommended_action = RECOMMENDED_ACTIONS[final_status]

    return {
        "failure_probability": round(failure_probability, 4),
        "ml_prediction": int(is_ml_failure),
        "final_status": final_status,
        "expert_score": int(score),
        "reasons": reasons,
        "recommended_action": recommended_action,
        "contributing_factors": contributing_factors
    }
