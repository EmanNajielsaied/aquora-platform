"""
Exhaustive Custom CSS Design System for Aquora Smart Water Infrastructure Dashboard.
Guarantees a 100% unified, coherent, engineering-grade dark theme across all Streamlit components:
- App container, main viewport, and full block layout
- Sidebar, header, toolbar, status decorations, and footer
- Tabs, tab lists, tab panels, columns, and metric cards
- Number inputs, text inputs, sliders, selectboxes, dropdown menus, and popovers
- Expanders, summaries, and inner expander details containers
- Buttons, progress bars, tables, dataframes, checkboxes, and alerts
Permanently eliminates any accidental white/black splits or unreadable contrast.
"""

def get_custom_css() -> str:
    return """
    <script>
    /* Ensure Streamlit active theme is locked to dark mode in browser storage */
    (function() {
        try {
            localStorage.setItem("stActiveTheme", JSON.stringify({"name": "dark"}));
        } catch(e) {}
    })();
    </script>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global Root Theme Variables & Streamlit Emotion Engine Variable Overrides */
    :root, html, body, [data-testid="stAppViewContainer"], .stApp, section[data-testid="stMain"], [data-testid="stSidebar"] {
        /* Standard Streamlit Internal Theme Keys (Forced Dark) */
        --primary-color: #0ea5e9 !important;
        --background-color: #070b14 !important;
        --secondary-background-color: #0f172a !important;
        --text-color: #f8fafc !important;
        --font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color-scheme: dark !important;

        /* Aquora Engineering Dark Palette */
        --color-bg-base: #070b14;
        --color-bg-sidebar: #0b1120;
        --color-bg-surface: #0f172a;
        --color-bg-elevated: #1e293b;
        --color-bg-input: #131d35;
        --color-border: rgba(56, 189, 248, 0.20);
        --color-border-glow: rgba(14, 165, 233, 0.45);
        --color-accent-cyan: #38bdf8;
        --color-accent-blue: #0284c7;
        --color-emerald: #10b981;
        --color-amber: #f59e0b;
        --color-rose: #f43f5e;
        --color-text-main: #f8fafc;
        --color-text-muted: #94a3b8;
        --color-text-dim: #64748b;
    }

    /* 1. Global Viewport & View Container (Guarantees NO white background leak anywhere) */
    html, body, [data-testid="stAppViewContainer"], .stApp, 
    section[data-testid="stMain"], div.stMain, [data-testid="stMainBlockContainer"], 
    .main, .block-container, [data-testid="stAppViewBlockContainer"] {
        background-color: #070b14 !important;
        background: radial-gradient(circle at 50% -10%, #0d1e38 0%, #070b14 100%) fixed !important;
        color: #f8fafc !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Main Block Container Width & Spacing */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 1360px !important;
    }

    /* 2. Top Header Bar & Decoration Elements */
    header[data-testid="stHeader"] {
        background: rgba(7, 11, 20, 0.90) !important;
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid rgba(56, 189, 248, 0.20) !important;
    }

    [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stBottom"], [data-testid="stStatusWidget"] {
        background: transparent !important;
        color: #f8fafc !important;
    }

    /* 3. Sidebar Complete Cohesive Styling */
    section[data-testid="stSidebar"], [data-testid="stSidebarContent"], [data-testid="stSidebarUserContent"], [data-testid="stSidebarNav"] {
        background-color: #0b1120 !important;
        background: linear-gradient(180deg, #0f172a 0%, #070b14 100%) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.20) !important;
        color: #f8fafc !important;
    }

    section[data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] li {
        color: #cbd5e1 !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(56, 189, 248, 0.20) !important;
    }

    /* 4. Top Brand Header Component */
    .aquora-brand-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.25rem 1.75rem;
        background: rgba(15, 23, 42, 0.92);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6);
    }

    .brand-title-wrap {
        display: flex;
        align-items: center;
        gap: 1.1rem;
    }

    .brand-icon {
        font-size: 2.3rem;
        filter: drop-shadow(0 0 14px rgba(56, 189, 248, 0.65));
    }

    .brand-title {
        font-size: 1.75rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        color: #ffffff !important;
    }

    .brand-title .accent {
        color: #38bdf8 !important;
    }

    .brand-subtitle {
        font-size: 0.86rem;
        color: #94a3b8 !important;
        margin: 0.2rem 0 0 0;
    }

    /* Live Gateway Status Pill */
    .status-pill-box {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        padding: 0.45rem 1.1rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399 !important;
    }

    .status-pill-box.offline {
        background: rgba(244, 63, 94, 0.12);
        border: 1px solid rgba(244, 63, 94, 0.4);
        color: #fb7185 !important;
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #34d399;
        box-shadow: 0 0 10px #34d399;
        display: inline-block;
        animation: pulse-ring 2s infinite;
    }

    .pulse-dot.offline {
        background-color: #fb7185;
        box-shadow: 0 0 10px #fb7185;
    }

    @keyframes pulse-ring {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.25); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }

    /* 5. Tabs Bar Complete Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background: #0f172a !important;
        padding: 8px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(56, 189, 248, 0.20) !important;
        margin-bottom: 1.5rem !important;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        color: #94a3b8 !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        transition: all 0.2s ease !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.06) !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.28) 0%, rgba(2, 132, 199, 0.18) 100%) !important;
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important;
        box-shadow: 0 0 16px rgba(14, 165, 233, 0.25) !important;
    }

    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #38bdf8 !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        background: transparent !important;
        padding-top: 0.5rem !important;
    }

    /* 6. Streamlit Expander Containers (Completely Dark Inside and Out) */
    [data-testid="stExpander"], [data-testid="stExpanderDetails"] {
        background: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.20) !important;
        border-radius: 12px !important;
        margin-bottom: 0.9rem !important;
        overflow: hidden !important;
    }

    [data-testid="stExpander"] > details {
        background: #0f172a !important;
        color: #f8fafc !important;
    }

    [data-testid="stExpander"] details[open] {
        background: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.35) !important;
    }

    [data-testid="stExpander"] summary {
        background: #131d35 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        padding: 0.75rem 1rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    [data-testid="stExpander"] summary:hover {
        background: #172442 !important;
        color: #38bdf8 !important;
    }

    [data-testid="stExpander"] [data-testid="stVerticalBlock"] {
        padding: 0.75rem 1rem !important;
        background: #0f172a !important;
    }

    /* 7. BaseWeb Inputs, Text Inputs, Number Inputs, and Selectboxes */
    .stTextInput input, .stNumberInput input, 
    div[data-baseweb="input"] input, div[data-baseweb="base-input"] input {
        background-color: #131d35 !important;
        color: #ffffff !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        border-radius: 8px !important;
        padding: 0.55rem 0.85rem !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    div[data-baseweb="input"], div[data-baseweb="base-input"] {
        background-color: #131d35 !important;
        border-color: rgba(56, 189, 248, 0.25) !important;
        border-radius: 8px !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus,
    div[data-baseweb="input"]:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.35) !important;
    }

    /* NumberInput +/- button controls */
    div[data-testid="stNumberInput"] button {
        background-color: #172442 !important;
        color: #ffffff !important;
        border-color: rgba(56, 189, 248, 0.25) !important;
    }

    div[data-testid="stNumberInput"] button:hover {
        background-color: #1e3158 !important;
        color: #38bdf8 !important;
    }

    /* Selectbox Complete Styling */
    div[data-testid="stSelectbox"] [data-baseweb="select"],
    [data-baseweb="select"], [data-baseweb="select"] > div {
        background-color: #131d35 !important;
        color: #ffffff !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        border-radius: 8px !important;
    }

    [data-baseweb="select"] * {
        background-color: transparent !important;
        color: #ffffff !important;
    }

    /* Dropdown Popover & Menu List */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.35) !important;
        border-radius: 10px !important;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.7) !important;
    }

    li[role="option"] {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        padding: 0.6rem 1rem !important;
    }

    li[role="option"]:hover, li[aria-selected="true"] {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
    }

    /* Slider Component Dark Styling */
    div[data-testid="stSlider"] {
        padding: 0.5rem 0 !important;
    }

    div[data-testid="stSlider"] [data-baseweb="slider"] {
        background: transparent !important;
    }

    div[data-testid="stSlider"] div[role="slider"] {
        background-color: #0ea5e9 !important;
        border: 2px solid #ffffff !important;
        box-shadow: 0 0 10px rgba(14, 165, 233, 0.6) !important;
    }

    div[data-testid="stSlider"] [data-testid="stSliderTickBarMin"],
    div[data-testid="stSlider"] [data-testid="stSliderTickBarMax"],
    div[data-testid="stSlider"] p, div[data-testid="stSlider"] span {
        color: #94a3b8 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
    }

    /* Checkbox Component */
    div[data-testid="stCheckbox"] {
        background: transparent !important;
    }

    div[data-testid="stCheckbox"] label {
        color: #e2e8f0 !important;
    }

    div[data-testid="stCheckbox"] [data-baseweb="checkbox"] span {
        border-color: rgba(56, 189, 248, 0.4) !important;
        background-color: #131d35 !important;
    }

    /* Labels & Widget Descriptions */
    label, [data-testid="stWidgetLabel"] p {
        color: #cbd5e1 !important;
        font-size: 0.86rem !important;
        font-weight: 600 !important;
    }

    /* 8. Buttons Styling */
    .stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(56, 189, 248, 0.45) !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.65rem 1.4rem !important;
        box-shadow: 0 4px 16px rgba(2, 132, 199, 0.35) !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 6px 22px rgba(14, 165, 233, 0.5) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
        border: 1px solid #38bdf8 !important;
        box-shadow: 0 4px 20px rgba(14, 165, 233, 0.45) !important;
    }

    /* 9. Telemetry & Metric Cards */
    .telemetry-card {
        background: #0f172a;
        border: 1px solid rgba(56, 189, 248, 0.22);
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4);
        transition: border-color 0.2s ease, transform 0.2s ease;
    }

    .telemetry-card:hover {
        border-color: rgba(14, 165, 233, 0.55);
        transform: translateY(-2px);
    }

    .telemetry-card-title {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
        margin-bottom: 0.35rem;
    }

    .telemetry-card-value {
        font-size: 2.1rem;
        font-weight: 800;
        color: #ffffff;
        font-family: 'JetBrains Mono', monospace;
    }

    .telemetry-card-unit {
        font-size: 0.95rem;
        color: #38bdf8;
        font-weight: 600;
        margin-left: 0.3rem;
    }

    .telemetry-card-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 0.35rem;
    }

    /* 10. Hero Result Metric Box */
    .hero-result-box {
        background: linear-gradient(145deg, #0f172a 0%, rgba(2, 132, 199, 0.22) 100%);
        border: 1px solid rgba(14, 165, 233, 0.5);
        border-radius: 18px;
        padding: 2.25rem 2rem;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.55);
    }

    .hero-metric-label {
        font-size: 1.05rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 800;
        color: #38bdf8;
        margin-bottom: 0.5rem;
    }

    .hero-metric-number {
        font-size: 3.8rem;
        font-weight: 900;
        color: #ffffff;
        font-family: 'JetBrains Mono', monospace;
        text-shadow: 0 0 28px rgba(56, 189, 248, 0.6);
        line-height: 1.1;
    }

    /* 11. Scientific Constraint & Research Disclaimer Box */
    .scientific-disclaimer-box {
        background: #111b2e;
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 1.1rem 1.35rem;
        margin: 1.25rem 0;
        font-size: 0.88rem;
        line-height: 1.6;
        color: #cbd5e1;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .scientific-disclaimer-box strong {
        color: #38bdf8;
        font-weight: 700;
    }

    /* 12. Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.45rem 1.1rem;
        border-radius: 8px;
        font-size: 0.92rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .badge-normal {
        background: rgba(16, 185, 129, 0.18);
        border: 1px solid #10b981;
        color: #34d399;
    }

    .badge-warning {
        background: rgba(245, 158, 11, 0.18);
        border: 1px solid #f59e0b;
        color: #fbbf24;
    }

    .badge-high-risk {
        background: rgba(249, 115, 22, 0.2);
        border: 1px solid #f97316;
        color: #fb923c;
    }

    .badge-critical {
        background: rgba(244, 63, 94, 0.22);
        border: 1px solid #f43f5e;
        color: #fda4af;
        animation: pulse-critical 1.8s infinite;
    }

    @keyframes pulse-critical {
        0% { box-shadow: 0 0 0 0 rgba(244, 63, 94, 0.6); }
        70% { box-shadow: 0 0 0 10px rgba(244, 63, 94, 0); }
        100% { box-shadow: 0 0 0 0 rgba(244, 63, 94, 0); }
    }

    /* 13. Operational Action Recommendation Banner */
    .action-recommendation-box {
        background: #0f172a;
        border-radius: 12px;
        padding: 1.35rem 1.6rem;
        margin: 1.25rem 0;
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-left: 5px solid #38bdf8;
    }

    .action-title {
        font-size: 0.92rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #38bdf8;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.6rem;
    }

    .action-text {
        font-size: 0.94rem;
        color: #e2e8f0;
        line-height: 1.65;
        margin: 0;
    }

    /* 14. Triggered Heuristic Rules */
    .rule-item {
        background: #131d35;
        border-left: 3px solid #38bdf8;
        border-radius: 0 8px 8px 0;
        padding: 0.75rem 1.1rem;
        margin-bottom: 0.6rem;
        font-size: 0.88rem;
        color: #e2e8f0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        border-top: 1px solid rgba(255, 255, 255, 0.04);
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }

    /* 15. Tables & DataFrames */
    [data-testid="stDataFrame"], [data-testid="stTable"], div[data-testid="stDataFrame"] > div {
        background: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.20) !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
    }

    /* 16. Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #0284c7 0%, #38bdf8 100%) !important;
    }

    /* 17. Alerts (Info, Warning, Error) */
    [data-testid="stAlert"] {
        background-color: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        color: #f8fafc !important;
        border-radius: 10px !important;
    }

    /* 18. Native Metrics Styling */
    div[data-testid="stMetric"] {
        background-color: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.20) !important;
        padding: 0.75rem 1rem !important;
        border-radius: 10px !important;
    }

    div[data-testid="stMetricValue"] > div {
        color: #ffffff !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMetricLabel"] > div > p {
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    </style>
    """
