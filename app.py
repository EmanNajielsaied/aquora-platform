"""
Aquora Water Infrastructure Platform - Root Entry Point
Primary launcher for Streamlit Community Cloud and local environments.
Directly executes the master dashboard with self-contained in-process ML inference,
eliminating localhost:8000 subprocess and runpy KeyError issues.
"""

import sys
from pathlib import Path

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Direct import avoids runpy.run_path() module isolation and KeyError issues in Streamlit
from aquora_ui.app import main

if __name__ == "__main__":
    main()
