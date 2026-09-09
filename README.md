---
title: Aquora Smart Water Infrastructure
emoji: 💧
colorFrom: blue
colorTo: cyan
sdk: docker
app_port: 7860
pinned: false
---

# 💧 Aquora Smart Water Infrastructure Platform

A production-grade, unified AI monitoring, leak detection, and predictive decision-support platform designed for smart municipal water distribution networks.

---

## 🏛️ End-to-End System Architecture

```
                                AQUORA PLATFORM
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        ↓                              ↓                              ↓
 💧 WATER QUALITY              🚨 LEAK DETECTION             📈 LEAK PREDICTION
 (ANN Continuous WQI)          (Operational SCADA)           (AI/ML & Expert System)
        │                              │                              │
        │ [pH, Turb, TDS, Temp]        │ [Real-Time Telemetry & Feeds] │ [66 Raw Telemetry Inputs]
        ▼                              ▼                              ▼
 ┌──────────────┐              ┌──────────────────────────┐    ┌──────────────┐
 │ ANN Pipeline │              │  Supervisory Monitoring  │    │ XGBoost Pipe │
 └──────┬───────┘              │  - System Condition      │    └──────┬───────┘
        │                      │  - Active Alerts & Assets│           │
        ▼                      │  - Sensor Telemetry Feeds│           ▼
 AI-Estimated WQI              │  - Detection Events Log  │    AI Leak Prob vs 0.3880
 (Continuous Index)            │  - Analytics & Spectra   │    (Prediction & Risk Level)
                               └──────────────────────────┘           │
                                                                      ▼
                                                               ┌──────────────────┐
                                                               │  Expert System   │
                                                               │  Supporting Layer│
                                                               └────────┬─────────┘
                                                                        │
                                                                        ▼
                                                             NORMAL / WARNING / HIGH RISK / CRITICAL
                                                             Action Protocol & Triggered Rules
```

---

## 🧩 Subsystem Specifications & Artifact Mapping

### 1. 💧 Water Quality Subsystem
- **Model Artifact**: `quality_aquora_water_quality_ann_4sensor.joblib`
- **Architecture**: scikit-learn Pipeline (`SimpleImputer(median)` → `StandardScaler()` → `MLPRegressor(64, 32)`)
- **Hardware Sensors (Exactly 4)**:
  1. `pH` (0.0 – 14.0)
  2. `Turbidity_NTU` (Nephelometric Turbidity Units)
  3. `TDS_mg_L` (Total Dissolved Solids, mg/L)
  4. `Temperature_C` (Water Temperature, °C)
- **Model Output**: `Water_Quality_Index` (Continuous numeric prediction)
- **Important Scientific Constraint**: No Safe/Unsafe threshold, contamination classification, or alarm logic is defined for this model. Results are strictly presented as **"AI-estimated Water Quality Index"**.

### 2. 🚨 Leak Detection Subsystem (Operational Monitoring Dashboard)
- **Purpose**: Real-time supervisory monitoring (SCADA) of the distribution network.
- **Components**:
  - **Supervisory Network Overview**: Operational status (Normal/Nominal), Active Alert Counters, Monitored Assets (20,000 pipes), 24h Detected Incidents.
  - **Active Sector & Pipe Telemetry Feed**: Real-time sector selector (Sector North-Alpha, Zone B, Zone C, etc.), live pipe condition, operational pressure, vibration RMS, anomaly score.
  - **Sensor Monitoring & Signal Spectra**: Multi-sensor engineering metrics, acoustic/vibration telemetry cards, dynamic FFT signal spectrum and pressure profile charts.
  - **Detection Events Log**: Filterable historical detection event registry with timestamps, pipe IDs, event classifications, risk scores, and telemetry flags.

### 3. 📈 Leak Prediction Subsystem (AI/ML Predictive Workspace + Integrated Expert System)
- **Primary AI/ML Model Artifact**: `detect_xgboost_model.ubj` / `detect_xgboost_model (1).pkl`
- **Preprocessor Artifact**: `detect_preprocessor (3).pkl` (transforms 66 raw features → 82 processed features)
- **Saved Decision Threshold**: `0.38803765177726746` (`detect_threshold.json`, F1-optimal on validation set)
- **Validation Metrics**: Accuracy: `92.51%`, Recall: `96.52%`, F1-Score: `73.51%`, ROC-AUC: `0.9608`
- **4 Logical Engineering Input Groups**:
  1. Asset & Pipe Information (Age, Condition Score, Material, Diameter, Depth)
  2. Hydraulic & Operational Metrics (Pressure, Pressure Deviation, Flow Indicators)
  3. Sensor Telemetry (Vibration RMS, Acoustic RMS, Sensor Anomaly Score)
  4. Historical & Risk Information (Previous Failures, Maintenance Indicators, Asset Risk Score)
- **Primary Outputs**:
  - Failure Probability
  - Saved Decision Threshold (`0.3880`)
  - Prediction (`Leak Detected` / `No Leak Detected`)
  - Risk Level (`Low`, `Medium`, `High`)
- **Key Analytical Indicators**: Pipe Age, Condition Score, Pressure, Pressure Deviation, Vibration RMS, Acoustic RMS, Sensor Anomaly Score, Asset Risk Score.
- **Integrated Supporting Expert System**:
  - Directly interprets the real ML probability, threshold, risk level, and telemetry against configured engineering rules (`backend/expert_rules.py`, `decision_system_config.json`).
  - Evaluates composite expert score (Normal < 4 pts, Warning 4–11 pts, High Risk 12–17 pts, Critical $\ge$ 18 pts).
  - Emits triggered rules, contributing factors, reasoning, and operational action protocols.
  - Empirical validation pool: `decision_logic_results.csv` (1,000 evaluated municipal pipe cases).

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.9 – 3.13
- Required dependencies installed:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Run Automated Verification Tests
Verify all model artifacts, schemas, and endpoints without launching servers:
```bash
python test_aquora_integration.py
```

### 3. Start Backend Service (Port 8000)
Run the unified FastAPI gateway:
```bash
python run_backend.py
```
- API Base URL: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### 4. Start Master UI Dashboard (Port 8501)
In a separate terminal, launch the Streamlit frontend:
```bash
python run_frontend.py
```
- Dashboard URL: `http://localhost:8501`

---

## 🔌 API Endpoints Summary

| Method | Endpoint | Subsystem | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | System | Health audit of all 3 subsystem models |
| `GET` | `/api/quality/info` | Water Quality | Specifications, metrics, presets, and scientific disclaimer |
| `POST` | `/api/quality/predict` | Water Quality | Compute continuous AI-estimated WQI from 4 sensors |
| `GET` | `/api/leak/schema` | Leak Detection | 66 raw features, 8 engineering groups, threshold, presets |
| `GET` | `/api/leak/metrics` | Leak Detection | XGBoost model metrics from `detect_xgboost_metrics.json` |
| `POST` | `/api/leak/predict` | Leak Detection | Run XGBoost pipeline (66 $\to$ 82) + Supporting Expert Analysis |
| `GET` | `/api/decision/config` | Expert System | Score thresholds, levels, and output fields |

---

## 🎨 Cohesive Dark Theme Design System

The Aquora UI features a custom dark engineering design system (`aquora_ui/shared/styles.py`) that strictly guarantees:
- One coherent dark color palette across all three tabs.
- Full theme overrides on Streamlit BaseWeb components, inputs, dropdowns, expanders, and tables.
- Zero accidental white/black splits or unreadable contrast.
