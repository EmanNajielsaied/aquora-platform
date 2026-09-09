"""
Module 3: 📈 Leak Prediction (AI/ML Leak/Failure Prediction + Integrated Supporting Expert System)
Primary AI/ML predictive analytics workspace for distribution pipeline failure assessment.
Runs the trained XGBoost classification pipeline (66 raw -> 82 transformed features)
evaluated strictly against the saved validation threshold (0.3880) from detect_threshold.json.
Integrated with the supporting Expert System decision logic layer to provide rule evaluation,
reasoning, final operational status, and recommended field actions.
"""

from typing import Dict, Any
import streamlit as st
import pandas as pd
from aquora_ui.shared.api_client import api_client
from aquora_ui.shared.components import (
    render_telemetry_card,
    render_status_badge,
    render_action_recommendation,
    render_triggered_rules
)

def render_leak_prediction_tab():
    st.markdown("### 📈 AI/ML Leak & Failure Prediction Workspace")
    st.caption(
        "Focuses on predicting future or potential distribution pipe failure risk using the trained "
        "supervised XGBoost classifier and preprocessing pipeline. "
        "Strictly evaluated against the saved F1-optimal threshold (0.3880) from detect_threshold.json. "
        "Integrated with a supporting Expert System heuristic evaluation layer for operational decision support."
    )

    # Fetch schema & presets from backend
    try:
        schema_data = api_client.get_leak_schema()
        presets = schema_data.get("presets", {})
        saved_threshold = schema_data.get("decision_threshold", 0.38803765177726746)
    except Exception as e:
        st.warning(f"Backend API connection unavailable: {e}. Using saved threshold ({0.3880}).")
        presets = {}
        saved_threshold = 0.38803765177726746

    # Presets Selection Bar
    st.markdown("##### ⚡ Benchmark Asset Scenarios")
    pcol1, pcol2 = st.columns([3, 1])

    with pcol1:
        preset_keys = list(presets.keys()) if presets else []
        if preset_keys:
            preset_names = [presets[k]["title"] for k in preset_keys]
            sel_idx = st.selectbox(
                "Select Asset Scenario",
                range(len(preset_names)),
                format_func=lambda i: preset_names[i],
                label_visibility="collapsed",
                key="leak_pred_preset_selector"
            )
            chosen_preset = presets[preset_keys[sel_idx]]
            st.caption(f"ℹ️ {chosen_preset['description']}")
        else:
            chosen_preset = None

    # Manage form state in session_state
    if "pred_features" not in st.session_state and chosen_preset:
        st.session_state.pred_features = dict(chosen_preset["data"])

    with pcol2:
        st.write("")
        if chosen_preset and st.button("Apply Scenario", key="btn_apply_pred_preset", use_container_width=True):
            st.session_state.pred_features = dict(chosen_preset["data"])
            st.rerun()

    features: Dict[str, Any] = st.session_state.get("pred_features", {})

    st.markdown("---")
    st.markdown("##### 🎛️ Predictive Model Inputs (Organized into 4 Engineering Groups)")

    # Group 1: Asset & Pipe Information
    with st.expander("🏢 1. Asset & Pipe Information", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            features["Asset_Type"] = st.selectbox(
                "Asset Type",
                ["MAIN", "SERVICE", "HYDRANT", "VALVE"],
                index=["MAIN", "SERVICE", "HYDRANT", "VALVE"].index(features.get("Asset_Type", "MAIN")) if features.get("Asset_Type") in ["MAIN", "SERVICE", "HYDRANT", "VALVE"] else 0,
                key="pred_asset_type"
            )
            features["Pipe_Material"] = st.selectbox(
                "Pipe Material",
                ["CI", "DI", "PVC", "PE", "Unknown"],
                index=["CI", "DI", "PVC", "PE", "Unknown"].index(features.get("Pipe_Material", "DI")) if features.get("Pipe_Material") in ["CI", "DI", "PVC", "PE", "Unknown"] else 1,
                key="pred_material"
            )
            features["Pipe_Diameter_cm"] = st.number_input("Pipe Diameter (cm)", value=float(features.get("Pipe_Diameter_cm", 68.0)), step=5.0, key="pred_diam")
        with col2:
            features["Pipe_Length_m"] = st.number_input("Pipe Length (m)", value=float(features.get("Pipe_Length_m", 80.0)), step=10.0, key="pred_len")
            features["Pipe_Depth_m"] = st.number_input("Pipe Depth (m)", value=float(features.get("Pipe_Depth_m", 1.35)), step=0.1, key="pred_depth")
            features["Frost_Depth_m"] = st.number_input("Frost Depth (m)", value=float(features.get("Frost_Depth_m", 0.76)), step=0.1, key="pred_frost")
        with col3:
            features["Pipe_Age_Years"] = st.number_input("Pipe Age (Years)", value=float(features.get("Pipe_Age_Years", 8.0)), step=1.0, key="pred_age")
            features["Condition_Score"] = st.slider("Structural Condition Score (0-100)", 0.0, 100.0, float(features.get("Condition_Score", 75.0)), step=1.0, key="pred_cond")
            features["Criticality"] = st.selectbox(
                "Network Criticality",
                ["Low", "Medium", "High", "Critical"],
                index=["Low", "Medium", "High", "Critical"].index(features.get("Criticality", "Medium")) if features.get("Criticality") in ["Low", "Medium", "High", "Critical"] else 1,
                key="pred_crit"
            )

        # Configuration flags row
        st.write("")
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            features["Lined"] = 1 if st.checkbox("Internal Lining", value=bool(features.get("Lined", 1)), key="pred_lined") else 0
        with c2:
            features["Undersized"] = 1 if st.checkbox("Undersized Section", value=bool(features.get("Undersized", 0)), key="pred_undersized") else 0
        with c3:
            features["Shallow_Main"] = 1 if st.checkbox("Shallow Bed", value=bool(features.get("Shallow_Main", 0)), key="pred_shallow") else 0
        with c4:
            features["Oversized"] = 1 if st.checkbox("Oversized Main", value=bool(features.get("Oversized", 0)), key="pred_oversized") else 0
        with c5:
            features["Cleaned"] = 1 if st.checkbox("Recently Cleaned", value=bool(features.get("Cleaned", 1)), key="pred_cleaned") else 0

    # Group 2: Hydraulic & Operational Metrics
    with st.expander("💧 2. Hydraulic & Operational Metrics", expanded=True):
        hcol1, hcol2, hcol3 = st.columns(3)
        with hcol1:
            features["Pressure"] = st.number_input("Operating Pressure (kPa)", value=float(features.get("Pressure", 466.7)), step=5.0, help="Pipeline head ~466 kPa (~4.66 bar)", key="pred_press")
            features["Flow_Rate"] = st.number_input("Discharge Flow Rate (L/s)", value=float(features.get("Flow_Rate", 24.5)), step=2.0, key="pred_flow")
        with hcol2:
            features["Pressure_Deviation"] = st.number_input("Pressure Deviation (kPa)", value=float(features.get("Pressure_Deviation", 0.0)), step=5.0, help="Drop of 20-60 kPa indicates orifice loss", key="pred_pdev")
            features["Flow_Deviation"] = st.number_input("Flow Rate Deviation (L/s)", value=float(features.get("Flow_Deviation", 0.0)), step=2.0, key="pred_fdev")
        with hcol3:
            features["Pressure_Change_Rate"] = st.number_input("Pressure Change Rate (kPa/s)", value=float(features.get("Pressure_Change_Rate", 0.0)), step=1.0, key="pred_pcr")
            features["Flow_Change_Rate"] = st.number_input("Flow Change Rate (L/s²)", value=float(features.get("Flow_Change_Rate", 0.0)), step=1.0, key="pred_fcr")

    # Group 3: Sensor Telemetry
    with st.expander("📊 3. Sensor Telemetry (Vibration, Acoustic & Anomaly)", expanded=True):
        scol1, scol2 = st.columns(2)
        with scol1:
            features["Vibration_RMS"] = st.slider("Vibration Sensor RMS (g)", 0.0, 5.0, float(features.get("Vibration_RMS", 0.94)), step=0.05, key="pred_vrms")
            features["Vibration_Energy"] = st.number_input("Vibration Energy", value=float(features.get("Vibration_Energy", 1.00)), step=0.1, key="pred_venergy")
            features["Vibration_Kurtosis"] = st.number_input("Vibration Kurtosis", value=float(features.get("Vibration_Kurtosis", 3.13)), step=0.5, key="pred_vkurt")
            features["Sensor_Anomaly_Score"] = st.slider("Sensor Anomaly Score (0-1)", 0.0, 1.0, float(features.get("Sensor_Anomaly_Score", 0.15)), step=0.02, key="pred_sanom")
        with scol2:
            features["Acoustic_RMS"] = st.slider("Acoustic Emission RMS", 0.0, 5.0, float(features.get("Acoustic_RMS", 0.67)), step=0.05, key="pred_arms")
            features["Acoustic_Energy"] = st.number_input("Acoustic Energy", value=float(features.get("Acoustic_Energy", 0.56)), step=0.1, key="pred_aenergy")
            features["Acoustic_Kurtosis"] = st.number_input("Acoustic Kurtosis", value=float(features.get("Acoustic_Kurtosis", 3.17)), step=0.5, key="pred_akurt")
            features["Asset_Risk_Score"] = st.slider("Asset Risk Score (0-1)", 0.0, 1.0, float(features.get("Asset_Risk_Score", 0.35)), step=0.02, key="pred_arisk")

    # Group 4: Historical & Risk Information
    with st.expander("📜 4. Historical Failures & Environmental Context", expanded=False):
        mcol1, mcol2 = st.columns(2)
        with mcol1:
            features["Previous_Failures"] = st.number_input("Cumulative Previous Failures", value=int(features.get("Previous_Failures", 0)), step=1, key="pred_pfail")
            features["Failures_Last_1_Year"] = st.number_input("Failures in Past 1 Year", value=int(features.get("Failures_Last_1_Year", 0)), step=1, key="pred_f1y")
            features["Failures_Last_3_Years"] = st.number_input("Failures in Past 3 Years", value=int(features.get("Failures_Last_3_Years", 0)), step=1, key="pred_f3y")
            features["Days_Since_Last_Failure"] = st.number_input("Days Since Last Incident", value=float(features.get("Days_Since_Last_Failure", 1825.0)), step=30.0, key="pred_daysfail")
        with mcol2:
            features["Temperature_C"] = st.number_input("Ambient Temperature (°C)", value=float(features.get("Temperature_C", 18.5)), step=1.0, key="pred_temp")
            features["Season"] = st.selectbox("Season", ["Spring", "Summer", "Autumn", "Winter"], index=["Spring", "Summer", "Autumn", "Winter"].index(features.get("Season", "Autumn")) if features.get("Season") in ["Spring", "Summer", "Autumn", "Winter"] else 2, key="pred_season")
            features["Day_of_Week"] = st.selectbox("Day of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], index=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(features.get("Day_of_Week", "Wednesday")) if features.get("Day_of_Week") in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] else 2, key="pred_dow")
            features["Hour"] = st.slider("Hour of Day (0-23)", 0, 23, int(features.get("Hour", 14)), key="pred_hour")

    # Primary Action Button
    st.write("")
    btn_predict = st.button("📈 Run AI/ML Leak / Failure Prediction", type="primary", use_container_width=True)

    prediction_result = None
    if btn_predict or "last_pred_result" not in st.session_state:
        with st.spinner("Executing trained XGBoost inference pipeline (66 raw -> 82 features)..."):
            try:
                res = api_client.predict_leak(features)
                prediction_result = res
                st.session_state.last_pred_result = res
            except Exception as e:
                st.error(f"Inference request failed: {e}")
                prediction_result = st.session_state.get("last_pred_result")

    if prediction_result:
        st.markdown("---")
        
        # -------------------------------------------------------------
        # SECTION 1: PRIMARY AI / ML LEAK PREDICTION
        # -------------------------------------------------------------
        st.markdown("#### 🚨 AI / ML LEAK PREDICTION (Primary Result)")
        st.caption("Direct output of the trained XGBoost model evaluated against the saved validation threshold (0.3880).")

        ai_data = prediction_result.get("ai_prediction", prediction_result)
        leak_prob = ai_data["leak_probability"]
        leak_pct = ai_data["leak_probability_percentage"]
        thresh = ai_data["decision_threshold"]
        thresh_pct = ai_data.get("decision_threshold_percentage", f"{thresh*100:.2f}%")
        is_leak = ai_data["prediction"]
        status_text = ai_data["status"]
        risk_level = ai_data["risk_level"]

        # Primary 4-Card Summary Grid
        rcol1, rcol2, rcol3, rcol4 = st.columns(4)
        with rcol1:
            st.markdown(f"""
            <div class="telemetry-card" style="border-top: 4px solid {'#f43f5e' if is_leak else '#10b981'};">
                <div class="telemetry-card-title">Model Classification</div>
                <div style="margin: 0.5rem 0;">
                    {render_status_badge(status_text)}
                </div>
                <div class="telemetry-card-sub">AI binary inference result</div>
            </div>
            """, unsafe_allow_html=True)

        with rcol2:
            st.markdown(f"""
            <div class="telemetry-card" style="border-top: 4px solid {'#f43f5e' if is_leak else '#38bdf8'};">
                <div class="telemetry-card-title">Leak / Failure Probability</div>
                <div class="telemetry-card-value" style="color: {'#f43f5e' if is_leak else '#38bdf8'};">
                    {leak_pct}
                </div>
                <div class="telemetry-card-sub">Raw: <code>{leak_prob:.4f}</code></div>
            </div>
            """, unsafe_allow_html=True)

        with rcol3:
            st.markdown(f"""
            <div class="telemetry-card" style="border-top: 4px solid #0284c7;">
                <div class="telemetry-card-title">Decision Threshold</div>
                <div class="telemetry-card-value" style="color: #38bdf8;">
                    {thresh:.4f}
                </div>
                <div class="telemetry-card-sub">Saved F1-Optimal (<code>{thresh_pct}</code>)</div>
            </div>
            """, unsafe_allow_html=True)

        with rcol4:
            st.markdown(f"""
            <div class="telemetry-card" style="border-top: 4px solid {'#f43f5e' if risk_level == 'High' else ('#f59e0b' if risk_level == 'Medium' else '#10b981')};">
                <div class="telemetry-card-title">Risk Level</div>
                <div style="margin: 0.5rem 0;">
                    {render_status_badge(risk_level)}
                </div>
                <div class="telemetry-card-sub">Telemetry risk index</div>
            </div>
            """, unsafe_allow_html=True)

        # Progress bar showing probability vs threshold
        st.write("")
        st.caption(f"Failure Probability relative to saved decision threshold ({thresh:.4f}):")
        st.progress(min(max(float(leak_prob), 0.0), 1.0))

        # -------------------------------------------------------------
        # SECTION 2: KEY RISK INDICATORS
        # -------------------------------------------------------------
        st.markdown("---")
        st.markdown("#### 🔍 KEY RISK INDICATORS")
        st.caption("Core analytical features monitored by the supervisory telemetry system.")

        indicators = prediction_result.get("key_indicators", {})
        kcol1, kcol2, kcol3, kcol4 = st.columns(4)

        with kcol1:
            render_telemetry_card("Pipe Age", indicators.get("Pipe_Age_Years", 0.0), "yrs", "Asset Age")
            render_telemetry_card("Operating Pressure", indicators.get("Pressure", 0.0), "kPa", "Operating Head")

        with kcol2:
            render_telemetry_card("Condition Score", indicators.get("Condition_Score", 0.0), "/100", "Physical Health")
            render_telemetry_card("Pressure Deviation", indicators.get("Pressure_Deviation", 0.0), "kPa", "Hydraulic Surge/Drop")

        with kcol3:
            render_telemetry_card("Vibration RMS", indicators.get("Vibration_RMS", 0.0), "g", "Structural RMS")
            render_telemetry_card("Sensor Anomaly", indicators.get("Sensor_Anomaly_Score", 0.0), "", "Signal Divergence")

        with kcol4:
            render_telemetry_card("Acoustic RMS", indicators.get("Acoustic_RMS", 0.0), "RMS", "Acoustic Energy")
            render_telemetry_card("Asset Risk Score", indicators.get("Asset_Risk_Score", 0.0), "", "Vulnerability Index")

        # -------------------------------------------------------------
        # SECTION 3: INTEGRATED SUPPORTING EXPERT SYSTEM ANALYSIS
        # -------------------------------------------------------------
        st.markdown("---")
        st.markdown("#### 🧠 EXPERT SYSTEM ANALYSIS (Supporting Decision Layer)")
        st.caption(
            "Operational decision support layer translating the AI prediction and telemetry into heuristic rule evaluation, "
            "contributing factor analysis, final operational status, and recommended field actions."
        )

        expert_data = prediction_result.get("expert_analysis", {})
        if expert_data:
            expert_score = expert_data.get("expert_score", 0)
            final_status = expert_data.get("final_status", "NORMAL")
            reasons = expert_data.get("reasons", [])
            recommended_action = expert_data.get("recommended_action", "")
            factors = expert_data.get("contributing_factors", [])

            # Expert Score & Status Card
            ecol1, ecol2 = st.columns([1, 2])
            with ecol1:
                st.markdown(f"""
                <div class="telemetry-card" style="border-top: 4px solid {'#f43f5e' if final_status == 'CRITICAL' else ('#f97316' if final_status == 'HIGH RISK' else ('#f59e0b' if final_status == 'WARNING' else '#10b981'))};">
                    <div class="telemetry-card-title">Composite Expert Score</div>
                    <div class="telemetry-card-value" style="color: {'#f43f5e' if final_status == 'CRITICAL' else ('#f97316' if final_status == 'HIGH RISK' else ('#fbbf24' if final_status == 'WARNING' else '#34d399'))};">
                        {expert_score} <span style="font-size: 1rem; color: #94a3b8; font-weight: 500;">pts</span>
                    </div>
                    <div style="margin: 0.5rem 0;">
                        {render_status_badge(final_status)}
                    </div>
                    <div class="telemetry-card-sub">
                        Status Hierarchy: NORMAL (&lt;4) • WARNING (4-11) • HIGH RISK (12-17) • CRITICAL (≥18)
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with ecol2:
                # Operational Action Box
                render_action_recommendation(recommended_action, final_status)

            # Triggered Rules
            st.write("")
            render_triggered_rules(reasons)

            # Contributing Factors Table
            if factors:
                st.write("")
                st.markdown("##### 📊 Contributing Indicator Breakdown")
                df_factors = pd.DataFrame(factors)
                st.dataframe(
                    df_factors.rename(columns={
                        "category": "Indicator Category",
                        "feature": "Telemetry Feature",
                        "value": "Observed Value",
                        "points": "Expert Points (+)"
                    }),
                    use_container_width=True,
                    hide_index=True
                )

        # Performance Validation Metrics Collapsible
        st.markdown("---")
        with st.expander("📊 Saved Model Performance Metrics (detect_xgboost_metrics.json)"):
            mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
            with mcol1:
                st.metric("Test Accuracy", "92.51%")
            with mcol2:
                st.metric("Recall (Sensitivity)", "96.52%")
            with mcol3:
                st.metric("F1-Score", "73.51%")
            with mcol4:
                st.metric("ROC-AUC", "0.9608")
            with mcol5:
                st.metric("PR-AUC", "0.6106")
