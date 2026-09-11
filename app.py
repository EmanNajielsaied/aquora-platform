"""
Aquora Water Infrastructure Platform - Root Entry Point
Primary launcher for Streamlit Community Cloud and local environments.
Directly executes the master dashboard in aquora_ui/app.py with self-contained
in-process ML inference, eliminating localhost:8000 subprocess dependencies.
"""

import sys
from pathlib import Path
import runpy

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Launch master UI
app_path = ROOT_DIR / "aquora_ui" / "app.py"
runpy.run_path(str(app_path), run_name="__main__")
