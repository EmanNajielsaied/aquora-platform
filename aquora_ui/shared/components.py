"""
Reusable UI Components for Aquora Water Infrastructure Dashboard.
"""

from typing import Dict, Any, List, Optional
import streamlit as st

def render_header(backend_status: Dict[str, Any]):
    """Renders the top brand header with live backend connection status."""
    is_online = backend_status.get("status") in ["online", "ready"]

    pill_class = "status-pill-box" if is_online else "status-pill-box offline"
    pulse_class = "pulse-dot" if is_online else "pulse-dot offline"
    if is_online:
        status_text = "API Gateway Online (Port 8000)" if backend_status.get("mode") == "http" else "API Gateway Online"
    else:
        status_text = "API Gateway Offline"

    st.markdown(f"""
    <div class="aquora-brand-header">
        <div class="brand-title-wrap">
            <div class="brand-icon">💧</div>
            <div>
                <h1 class="brand-title">AQUORA <span class="accent">INFRASTRUCTURE</span></h1>
                <p class="brand-subtitle">Smart Water Management & Predictive Engineering System</p>
            </div>
        </div>
        <div class="{pill_class}">
            <span class="{pulse_class}"></span>
            <span>{status_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_telemetry_card(title: str, value: Any, unit: str = "", subtitle: str = ""):
    """Renders a single telemetry sensor card."""
    formatted_val = f"{value:.2f}" if isinstance(value, float) else str(value)
    st.markdown(f"""
    <div class="telemetry-card">
        <div class="telemetry-card-title">{title}</div>
        <div class="telemetry-card-value">{formatted_val}<span class="telemetry-card-unit">{unit}</span></div>
        {f'<div class="telemetry-card-sub">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_status_badge(status: str) -> str:
    """Returns HTML for a colored status badge."""
    norm = status.strip().upper()
    if norm in ["NORMAL", "NO LEAK DETECTED", "NORMAL OPERATION", "LOW"]:
        badge_class = "badge-normal"
        icon = "✓"
    elif norm in ["WARNING", "MEDIUM"]:
        badge_class = "badge-warning"
        icon = "⚠"
    elif norm in ["HIGH RISK", "HIGH"]:
        badge_class = "badge-high-risk"
        icon = "⚡"
    else:  # CRITICAL, LEAK DETECTED, FAILURE EXPECTED
        badge_class = "badge-critical"
        icon = "🚨"

    return f'<span class="status-badge {badge_class}">{icon} {status}</span>'

def render_scientific_notice(text: str):
    """Renders a formatted academic research disclaimer."""
    st.markdown(f"""
    <div class="scientific-disclaimer-box">
        <strong>SCIENTIFIC CONSTRAINT & RESEARCH NOTICE:</strong><br/>
        {text}
    </div>
    """, unsafe_allow_html=True)

def render_action_recommendation(action_text: str, status_level: str):
    """Renders operational engineering recommendation banner."""
    st.markdown(f"""
    <div class="action-recommendation-box">
        <div class="action-title">
            <span>🛡️ Operational Action Protocol ({status_level})</span>
        </div>
        <p class="action-text">{action_text}</p>
    </div>
    """, unsafe_allow_html=True)

def render_triggered_rules(rules: List[str]):
    """Renders the list of triggered decision rules."""
    if not rules:
        return
    st.markdown("##### 📜 Reasoning & Triggered Heuristic Rules")
    for rule in rules:
        st.markdown(f"""
        <div class="rule-item">
            <span>🔹</span>
            <span>{rule}</span>
        </div>
        """, unsafe_allow_html=True)
