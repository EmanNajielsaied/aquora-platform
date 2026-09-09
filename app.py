"""
Aquora Platform - Root Entry Point for Streamlit
Launches the master dashboard located in aquora_ui/app.py.
"""

from pathlib import Path
import runpy

app_path = Path(__file__).resolve().parent / "aquora_ui" / "app.py"
runpy.run_path(str(app_path), run_name="__main__")
