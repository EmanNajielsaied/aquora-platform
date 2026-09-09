"""
Module 3: Expert System / Decision Logic
Dedicated supporting decision and explanation interface exploring the expert rule hierarchy,
conceptual decision flow, decision thresholds, active asset rule inspection,
and historical empirical validation results (decision_logic_results.csv).
Acts strictly as a supporting operational layer on top of the primary Leak / Failure Prediction.
"""

from typing import Dict, Any, List
from pathlib import Path
import streamlit as st
import pandas as pd

from aquora_ui.shared.api_client import api_client
from aquora_ui.shared.components import (
    render_telemetry_card,
    render_status_badge,
    render_action_recommendation,
    render_triggered_rules
)

def render_decision_system_tab():
    st.markdown("### 🧠 Expert System & Decision Logic Architecture")
    st.caption(
        "Supporting operational decision layer designed to translate AI/ML leak predictions and supervisory telemetry "
        "into rule-based operational safety evaluations, reasoning, and field escalation protocols."
    )

    # -------------------------------------------------------------
    # 1. CONCEPTUAL ARCHITECTURE FLOW DIAGRAM
    # -------------------------------------------------------------
    st.markdown("#### 🔄 End-to-End Decision Flow")
    st.markdown("""
    ```
    ┌────────────────────────────────────────────────────────────────────────┐
    │ 📡 Sensors / Telemetry Inputs (Acoustic, Vibration, Pressure, Asset)   │
    └───────────────────────────────────┬────────────────────────────────────┘
                                        │
                                        ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │ 🚨 Primary AI / ML Leak Prediction (Trained XGBoost Pipeline)          │
    │    • Raw Features: 66 → Transformed: 82                                │
    │    • Evaluates Probability against Saved Threshold: 0.3880             │
    └───────────────────────────────────┬────────────────────────────────────┘
                                        │
                                        ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │ 📊 Leak / Failure Probability & Risk Level                             │
    │    • Probability [actual] • Threshold [0.3880] • Risk Level [actual]   │
    └───────────────────────────────────┬────────────────────────────────────┘
                                        │
                                        ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │ 🧠 Expert System Rules Engine (decision_system_config.json)            │
    │    • AI Probability Contribution (+2 to +6 pts)                        │
    │    • Asset Structural Aging & Condition (+1 to +3 pts)                 │
    │    • Hydraulic Surge & Pressure Deviation (+1 to +3 pts)               │
    │    • Acoustic & Vibration Telemetry Energy (+1 to +3 pts)              │
    │    • Historical Incident Frequency & Recurrence (+1 to +3 pts)         │
    └───────────────────────────────────┬────────────────────────────────────┘
                                        │
                                        ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │ 🎯 Final Operational Decision & Recommended Action                     │
    │    • NORMAL (< 4) • WARNING (4-11) • HIGH RISK (12-17) • CRITICAL (≥18)│
    └────────────────────────────────────────────────────────────────────────┘
    ```
    """)

    # -------------------------------------------------------------
    # 2. EXPERT SCORE HIERARCHY & CALIBRATION MATRIX
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown("#### 📐 Expert Score Levels (decision_system_config.json)")
    st.caption("Standardized point threshold hierarchy governing municipal water distribution escalation protocols.")

    scol1, scol2, scol3, scol4 = st.columns(4)
    with scol1:
        st.markdown("""
        <div class="telemetry-card" style="border-top: 3px solid #10b981;">
            <div class="telemetry-card-title">Level 1: Normal</div>
            <div class="telemetry-card-value" style="color: #34d399;">&lt; 4 <span style="font-size: 0.9rem; color: #94a3b8;">pts</span></div>
            <div class="telemetry-card-sub">Baseline quarterly SCADA logging & preventive maintenance.</div>
        </div>
        """, unsafe_allow_html=True)
    with scol2:
        st.markdown("""
        <div class="telemetry-card" style="border-top: 3px solid #f59e0b;">
            <div class="telemetry-card-title">Level 2: Warning</div>
            <div class="telemetry-card-value" style="color: #fbbf24;">4 - 11 <span style="font-size: 0.9rem; color: #94a3b8;">pts</span></div>
            <div class="telemetry-card-sub">Bi-hourly sensor sampling & acoustic survey within 14 days.</div>
        </div>
        """, unsafe_allow_html=True)
    with scol3:
        st.markdown("""
        <div class="telemetry-card" style="border-top: 3px solid #f97316;">
            <div class="telemetry-card-title">Level 3: High Risk</div>
            <div class="telemetry-card-value" style="color: #fb923c;">12 - 17 <span style="font-size: 0.9rem; color: #94a3b8;">pts</span></div>
            <div class="telemetry-card-sub">Dispatch field crew in 48h; restrict local line pressure.</div>
        </div>
        """, unsafe_allow_html=True)
    with scol4:
        st.markdown("""
        <div class="telemetry-card" style="border-top: 3px solid #f43f5e;">
            <div class="telemetry-card-title">Level 4: Critical</div>
            <div class="telemetry-card-value" style="color: #fda4af;">&ge; 18 <span style="font-size: 0.9rem; color: #94a3b8;">pts</span></div>
            <div class="telemetry-card-sub">Immediate sectional isolation & emergency repair mobilization.</div>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 3. ACTIVE PIPELINE ASSET & LIVE RULE EVALUATION
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown("#### 🔍 Active Pipeline Asset: Live Rule & Decision Inspection")
    st.caption(
        "Synchronized with the primary Leak / Failure Prediction module. "
        "Shows how the AI prediction and active telemetry trigger specific domain rules."
    )

    last_leak = st.session_state.get("last_leak_result")
    
    if last_leak:
        ai_data = last_leak.get("ai_prediction", last_leak)
        expert_data = last_leak.get("expert_analysis", {})

        c1, c2 = st.columns([1, 1.25])
        with c1:
            st.markdown(f"""
            <div class="telemetry-card" style="border-top: 4px solid #38bdf8;">
                <div class="telemetry-card-title">Active AI Leak Prediction</div>
                <div class="telemetry-card-value" style="color: {'#f43f5e' if ai_data.get('prediction') else '#38bdf8'};">
                    {ai_data.get('leak_probability_percentage', 'N/A')}
                </div>
                <div style="margin: 0.5rem 0;">
                    {render_status_badge(ai_data.get('status', ''))}
                </div>
                <div class="telemetry-card-sub">
                    Saved Threshold: <strong>{ai_data.get('decision_threshold', 0.3880):.4f}</strong> • 
                    Risk Level: <strong>{ai_data.get('risk_level', 'N/A')}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="telemetry-card" style="border-top: 4px solid {'#f43f5e' if expert_data.get('final_status') == 'CRITICAL' else '#10b981'};">
                <div class="telemetry-card-title">Supporting Expert Evaluation</div>
                <div class="telemetry-card-value" style="color: {'#f43f5e' if expert_data.get('final_status') == 'CRITICAL' else ('#fbbf24' if expert_data.get('final_status') == 'WARNING' else '#34d399')};">
                    {expert_data.get('expert_score', 0)} <span style="font-size: 1rem; color: #94a3b8;">pts</span>
                </div>
                <div style="margin: 0.5rem 0;">
                    {render_status_badge(expert_data.get('final_status', 'NORMAL'))}
                </div>
                <div class="telemetry-card-sub">
                    Evaluated from {len(expert_data.get('reasons', []))} rule criteria
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Operational Action Protocol
        render_action_recommendation(
            expert_data.get("recommended_action", "Standard operating protocol."),
            expert_data.get("final_status", "NORMAL")
        )

        # Triggered Heuristic Rules
        render_triggered_rules(expert_data.get("reasons", []))

        # Contributing Factors Table
        factors = expert_data.get("contributing_factors", [])
        if factors:
            st.write("")
            st.markdown("##### 📊 Contributing Indicator Points Breakdown")
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
    else:
        st.info(
            "ℹ️ No active prediction session found. Navigate to **🚨 Leak / Failure Prediction** to run a prediction, "
            "or apply one of the benchmark presets to inspect the rule firing in real time."
        )

    # -------------------------------------------------------------
    # 4. HISTORICAL VALIDATION BENCHMARK (decision_logic_results.csv)
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown("#### 📊 Empirical Validation Pool (decision_logic_results.csv)")
    st.caption("Statistical distribution across 1,000 empirical pipe assessment cases evaluated through the ML model and Expert System.")

    results_csv_path = Path(__file__).resolve().parent.parent.parent / "decision_logic_results.csv"
    if results_csv_path.exists():
        df_results = pd.read_csv(results_csv_path)

        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        counts = df_results["final_status"].value_counts()
        with mcol1:
            render_telemetry_card("Normal Cases", counts.get("NORMAL", 0), "", "51.3% of validation pool")
        with mcol2:
            render_telemetry_card("Warning Cases", counts.get("WARNING", 0), "", "44.1% of validation pool")
        with mcol3:
            render_telemetry_card("High Risk Cases", counts.get("HIGH RISK", 0), "", "4.0% of validation pool")
        with mcol4:
            render_telemetry_card("Critical Emergencies", counts.get("CRITICAL", 0), "", "0.6% of validation pool")

        with st.expander("🔍 Inspect Empirical Validation Cases Table"):
            st.dataframe(
                df_results.head(25).rename(columns={
                    "index": "Asset Case #",
                    "failure_probability": "ML Failure Prob",
                    "ml_prediction": "ML Binary Class",
                    "expert_score": "Expert Score",
                    "final_status": "Operational Status"
                }),
                use_container_width=True,
                hide_index=True
            )

    # -------------------------------------------------------------
    # 5. DOMAIN RULE MATRIX SPECIFICATION
    # -------------------------------------------------------------
    with st.expander("📖 Inspect Configured Domain Rules & Scoring Weights"):
        st.markdown("""
        | Rule Category | Condition / Threshold | Points | Operational Rationale |
        | :--- | :--- | :---: | :--- |
        | **AI Prediction** | Failure Prob $\ge$ 85% | **+6** | Severe machine learning failure confidence |
        | **AI Prediction** | Failure Prob $\ge$ Model Threshold (0.3880) | **+5** | Supervised model classifies active leak/failure |
        | **AI Prediction** | Failure Prob $\ge$ 35% | **+2** | Moderate risk tendency approaching threshold |
        | **Asset Health** | Pipe Age $\ge$ 50 years | **+3** | Severe structural embrittlement and fatigue |
        | **Asset Health** | Condition Score $\le$ 2.5 / 10 | **+3** | Critical wall thinning / internal pitting |
        | **Asset Health** | Criticality = 'Critical' | **+2** | High consequence of failure for municipal district |
        | **Asset Health** | Pipe Material = 'CI' (Cast Iron) | **+1** | Legacy brittle metallic pipe class |
        | **Hydraulics** | Pressure Deviation $\ge$ 2.0 bar | **+3** | Major hydraulic surge or pressure breach |
        | **Telemetry** | Acoustic RMS $\ge$ 2.0 | **+3** | High-frequency continuous leak hiss signature |
        | **Telemetry** | Vibration RMS $\ge$ 1.8 g | **+3** | Violent mechanical resonance or cavitation |
        | **Telemetry** | Acoustic Kurtosis $\ge$ 8.0 | **+1** | Transient shock waves from joint loosening |
        | **History** | Failures in Last Year $\ge$ 2 | **+3** | Chronic repeated failure zone |
        | **History** | Days Since Last Failure $\le$ 90 days | **+1** | Vulnerable recent repair zone |
        | **Anomaly** | Sensor Anomaly Score $\ge$ 0.80 | **+2** | Sensor divergence from hydraulic equilibrium |
        """)
