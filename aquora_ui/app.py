"""
Aquora Water Infrastructure Platform - Unified Master Dashboard
Integrates THREE core navigation sections:
1. 💧 Water Quality Subsystem (ANN 4-sensor WQI continuous numeric prediction)
2. 🚨 Leak Detection Subsystem (Complete SCADA telemetry, events, and anomaly monitoring dashboard)
3. 📈 Leak Prediction Subsystem (Primary AI/ML predictive analytics + integrated supporting Expert System)
"""

import sys
from pathlib import Path

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from aquora_ui.shared.styles import get_custom_css
from aquora_ui.shared.api_client import api_client
from aquora_ui.shared.components import render_header
from aquora_ui.water_quality.view import render_water_quality_tab
from aquora_ui.leak_detection.view import render_leak_detection_tab
from aquora_ui.leak_prediction.view import render_leak_prediction_tab


def main():
    # Configure Page
    st.set_page_config(
        page_title="Aquora | Smart Water Infrastructure Platform",
        page_icon="💧",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Inject Custom Cohesive Dark CSS Theme
    st.markdown(get_custom_css(), unsafe_allow_html=True)

    # Ping Backend API Gateway / In-Process Engine
    backend_status = api_client.check_health()

    # Render Top Brand Header
    render_header(backend_status)

    # Sidebar System Navigation & Architecture Overview
    with st.sidebar:
        st.markdown("### 🏢 Aquora System Navigation")
        st.caption("University Water Infrastructure Research & Deployment Platform")

        st.markdown("---")
        st.markdown("##### 📡 Subsystem Gateway Audit")

        is_online = backend_status.get("status") in ["online", "ready"]
        if is_online:
            mode_str = " (Port 8000)" if backend_status.get("mode") == "http" else " (Direct Engine)"
            st.success(f"✓ FastAPI Gateway Connected{mode_str}")
            subsystems = backend_status.get("subsystems", {})
            for key, sub in subsystems.items():
                status_symbol = "🟢" if sub.get("status") == "ready" else "🔴"
                st.markdown(f"{status_symbol} **{sub.get('name')}** (`{sub.get('target', '')}`)")
        else:
            st.error("❌ FastAPI Backend Disconnected")
            st.info("Start backend with: `python run_backend.py`")

        st.markdown("---")
        st.markdown("##### 🔬 Architectural Framework")
        st.markdown("""
        **1. 💧 Water Quality:**
        - Sensors: pH, Turbidity, TDS, Temp
        - Pipeline: ANN (`MLPRegressor`)
        - Output: Continuous WQI
        - Constraint: *Strict empirical numeric index (No safe/unsafe threshold)*

        **2. 🚨 Leak Detection:**
        - Role: Operational Monitoring Dashboard
        - Telemetry: Pressure, Flow, Vibration, Acoustics, Sensor Anomaly
        - Coverage: 20,000 SCADA nodes
        - Features: Real-time alerts, event logs, analytical profiles

        **3. 📈 Leak Prediction:**
        - Role: AI/ML Predictive Analytics
        - Inputs: 66 raw features → 82 transformed features
        - Model: XGBoost Classifier (Threshold: **0.3880**)
        - Integrated: Supporting Expert System decision layer & rule evaluation
        """)

        st.markdown("---")
        st.caption("Aquora Platform • Engineering & Research 2026")

    # Render Exactly Three Main Navigation Tabs
    tab_quality, tab_detection, tab_prediction = st.tabs([
        "💧 Water Quality",
        "🚨 Leak Detection",
        "📈 Leak Prediction"
    ])

    with tab_quality:
        render_water_quality_tab()

    with tab_detection:
        render_leak_detection_tab()

    with tab_prediction:
        render_leak_prediction_tab()


if __name__ == "__main__":
    main()
