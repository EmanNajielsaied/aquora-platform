"""
Water Quality Subsystem View
Displays current readings from the four physical sensors and continuous AI-estimated WQI.
Complies strictly with the scientific constraint prohibiting safe/unsafe or contamination labels.
"""

import streamlit as st
from aquora_ui.shared.api_client import api_client
from aquora_ui.shared.components import (
    render_telemetry_card,
    render_scientific_notice
)

def render_water_quality_tab():
    st.markdown("### 💧 Physical 4-Sensor Water Quality Telemetry")
    st.caption(
        "Direct telemetry monitoring from the 4 physical hardware sensors installed on the Aquora testbed. "
        "Estimated via ANN / MLPRegressor scikit-learn pipeline."
    )

    # Fetch metadata and presets from backend
    try:
        info_data = api_client.get_water_quality_info()
        presets = info_data.get("presets", {})
    except Exception as e:
        st.warning(f"Could not reach backend API at {api_client.base_url}. Using local preset defaults.")
        presets = {
            "optimal_potable": {
                "title": "Baseline Finished Tap Water",
                "description": "Typical municipal treated distribution water.",
                "sensors": {"pH": 7.4, "Turbidity_NTU": 0.8, "TDS_mg_L": 180.0, "Temperature_C": 19.5}
            },
            "turbid_runoff": {
                "title": "Stormwater Runoff / High Turbidity",
                "description": "Particulate suspension and sediment influx.",
                "sensors": {"pH": 6.7, "Turbidity_NTU": 16.5, "TDS_mg_L": 380.0, "Temperature_C": 22.0}
            },
            "high_tds_mineral": {
                "title": "High TDS / Hard Water Stream",
                "description": "Dissolved mineral salt concentration profile.",
                "sensors": {"pH": 8.4, "Turbidity_NTU": 3.2, "TDS_mg_L": 890.0, "Temperature_C": 25.5}
            }
        }

    # Preset Selector
    st.markdown("##### ⚡ Quick Benchmark Telemetry Presets")
    col_preset, col_btn = st.columns([3, 1])
    with col_preset:
        preset_keys = list(presets.keys())
        preset_names = [presets[k]["title"] for k in preset_keys]
        selected_idx = st.selectbox(
            "Select Benchmark Scenario",
            range(len(preset_names)),
            format_func=lambda i: preset_names[i],
            label_visibility="collapsed"
        )
        chosen_preset = presets[preset_keys[selected_idx]]
        st.caption(f"ℹ️ {chosen_preset['description']}")

    # Initialize or update session state from preset
    if "wq_ph" not in st.session_state:
        st.session_state.wq_ph = chosen_preset["sensors"]["pH"]
        st.session_state.wq_turb = chosen_preset["sensors"]["Turbidity_NTU"]
        st.session_state.wq_tds = chosen_preset["sensors"]["TDS_mg_L"]
        st.session_state.wq_temp = chosen_preset["sensors"]["Temperature_C"]

    with col_btn:
        st.write("")  # Spacing
        if st.button("Apply Preset", use_container_width=True):
            st.session_state.wq_ph = chosen_preset["sensors"]["pH"]
            st.session_state.wq_turb = chosen_preset["sensors"]["Turbidity_NTU"]
            st.session_state.wq_tds = chosen_preset["sensors"]["TDS_mg_L"]
            st.session_state.wq_temp = chosen_preset["sensors"]["Temperature_C"]
            st.rerun()

    st.markdown("---")

    # 4 Sensor Inputs Form
    st.markdown("##### 🎛️ Active Sensor Parameter Controls")
    col1, col2 = st.columns(2)

    with col1:
        ph_val = st.slider(
            "1. pH Sensor (Acidity / Alkalinity)",
            min_value=0.0,
            max_value=14.0,
            value=float(st.session_state.wq_ph),
            step=0.05,
            help="Measured pH index. Typical drinking water range is 6.5 to 8.5."
        )
        turbidity_val = st.slider(
            "2. Turbidity Sensor (NTU)",
            min_value=0.0,
            max_value=50.0,
            value=float(st.session_state.wq_turb),
            step=0.1,
            help="Nephelometric Turbidity Units measuring suspended particles."
        )

    with col2:
        tds_val = st.slider(
            "3. Total Dissolved Solids (TDS, mg/L)",
            min_value=0.0,
            max_value=2000.0,
            value=float(st.session_state.wq_tds),
            step=5.0,
            help="Total dissolved mobile ions and dissolved minerals in mg/L."
        )
        temp_val = st.slider(
            "4. Water Temperature (°C)",
            min_value=-5.0,
            max_value=45.0,
            value=float(st.session_state.wq_temp),
            step=0.5,
            help="Continuous temperature reading from thermal probe."
        )

    # Inference Button
    st.write("")
    btn_predict = st.button("📊 Calculate AI-estimated Water Quality Index", type="primary", use_container_width=True)

    # Perform prediction
    payload = {
        "pH": ph_val,
        "Turbidity_NTU": turbidity_val,
        "TDS_mg_L": tds_val,
        "Temperature_C": temp_val
    }

    wqi_result = None
    if btn_predict or "last_wqi" not in st.session_state:
        with st.spinner("Processing 4-sensor ANN regression pipeline..."):
            try:
                res = api_client.predict_water_quality(payload)
                wqi_result = res["water_quality_index"]
                st.session_state.last_wqi = wqi_result
                st.session_state.last_payload = payload
            except Exception as e:
                st.error(f"Inference request failed: {e}")
                if "last_wqi" in st.session_state:
                    wqi_result = st.session_state.last_wqi

    if wqi_result is not None:
        st.markdown("---")
        st.markdown("#### 📈 AI Model Prediction & Telemetry Output")

        # 4 Current Sensor Telemetry Cards
        tcol1, tcol2, tcol3, tcol4 = st.columns(4)
        with tcol1:
            render_telemetry_card("pH Level", ph_val, "pH", "Acidity Index")
        with tcol2:
            render_telemetry_card("Turbidity", turbidity_val, "NTU", "Particulate Density")
        with tcol3:
            render_telemetry_card("TDS Reading", tds_val, "mg/L", "Dissolved Minerals")
        with tcol4:
            render_telemetry_card("Temperature", temp_val, "°C", "Core Thermal Probe")

        # Prominent Result Card with Exact Required Wording
        st.markdown(f"""
        <div class="hero-result-box">
            <div class="hero-metric-label">AI-estimated Water Quality Index</div>
            <div class="hero-metric-number">{wqi_result:.2f}</div>
            <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 0.5rem;">
                Continuous numeric index generated by the 4-sensor multi-layer perceptron regression pipeline.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Mandatory Scientific Constraint Box
        render_scientific_notice(
            "There is currently NO Safe/Unsafe threshold, contamination classification, or alarm logic defined for this model. "
            "In strict accordance with project research constraints, this output represents an <strong>AI-estimated Water Quality Index</strong> "
            "and must NOT be interpreted as an independently validated proof of contamination or drinking suitability."
        )

        # Model Architecture & Validation Specs Card
        with st.expander("🔬 Model Specifications & Cross-Validation Metrics"):
            mcol1, mcol2 = st.columns(2)
            with mcol1:
                st.markdown("""
                **Pipeline Architecture:**
                - Pipeline: `SimpleImputer(median)` → `StandardScaler()` → `MLPRegressor`
                - Hidden Layer Sizes: `(64, 32)`
                - Activation Function: `relu`
                - Solver: `adam` (batch size: 256)
                - Artifact: `quality_aquora_water_quality_ann_4sensor.joblib`
                """)
            with mcol2:
                st.markdown("""
                **Empirical Evaluation Performance:**
                - 5-Fold Group Cross Validation:
                  - $R^2$: `0.5818`
                  - RMSE: `3.1005`
                  - MAE: `2.4500`
                - Untouched Test Set:
                  - $R^2$: `0.5771` | RMSE: `3.0872` | MAE: `2.4349`
                """)

        # Future Sensor Expansion Roadmap
        with st.expander("📡 Future Hardware Sensor Expansion Candidates (Research Roadmap)"):
            st.markdown("""
            The Aquora physical testbed is currently equipped with exactly **four operational sensors** (pH, Turbidity, TDS, and Temperature). 
            Broader exploratory research indicates the following auxiliary water-quality metrics can provide supplementary fidelity upon future hardware deployment:

            | Auxiliary Parameter | Unit | Testbed Status | Research Role |
            | :--- | :--- | :--- | :--- |
            | **Dissolved Oxygen (DO)** | mg/L | *Future Expansion Candidate* | Bio-respiration and biological stability indicator |
            | **Electrical Conductivity (EC)** | µmhos/cm | *Future Expansion Candidate* | Ionic salinity and dissolved mineral validation |
            | **Biological Oxygen Demand (BOD)** | mg/L | *Future Expansion Candidate* | Organic load and effluent breakdown index |
            | **Nitrate & Nitrite ($NO_x$)** | mg/L | *Future Expansion Candidate* | Agricultural fertilizer runoff tracing |
            | **Coliform Organisms (Fecal & Total)** | MPN/100mL | *Future Expansion Candidate* | Biological ingress and cross-contamination tracing |

            > **Engineering Boundary:** In strict compliance with hardware boundaries, these auxiliary parameters are **not** present on current production nodes and are strictly excluded from the active ANN model inputs.
            """)
