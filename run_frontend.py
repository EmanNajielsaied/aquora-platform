"""
Aquora Platform - Frontend UI Launcher
Runs Streamlit on port 8501.
"""

import sys
import subprocess

if __name__ == "__main__":
    print("=" * 60)
    print("💧 STARTING AQUORA STREAMLIT MASTER DASHBOARD")
    print("=" * 60)
    print("🌐 Dashboard URL: http://localhost:8501")
    print("🔗 Connecting to FastAPI Backend: http://localhost:8000")
    print("=" * 60)
    cmd = [
        sys.executable, "-m", "streamlit", "run", "aquora_ui/app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--theme.base=dark",
        "--theme.primaryColor=#0ea5e9",
        "--theme.backgroundColor=#070b14",
        "--theme.secondaryBackgroundColor=#0f172a",
        "--theme.textColor=#f8fafc"
    ]
    subprocess.run(cmd)
