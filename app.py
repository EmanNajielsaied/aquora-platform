"""
Aquora Platform - Root Entry Point for Streamlit & Cloud Deployments
Automatically ensures the FastAPI backend is running in the cloud environment,
then launches the master dashboard located in aquora_ui/app.py.
"""

import os
import sys
import time
import subprocess
import urllib.request
from pathlib import Path
import runpy

def ensure_backend_running():
    """Verify backend is reachable; if not and targeting local, launch in background."""
    api_url = os.environ.get("AQUORA_API_URL", "http://127.0.0.1:8000")
    if not any(local_host in api_url for local_host in ["127.0.0.1", "localhost", "0.0.0.0"]):
        return  # Target is an external public API, do not start local process
    
    # Check if backend is already responding
    clean_url = api_url.rstrip("/")
    try:
        with urllib.request.urlopen(f"{clean_url}/api/health", timeout=1.0) as resp:
            if resp.getcode() == 200:
                return  # Backend already healthy
    except Exception:
        pass

    # Launch FastAPI backend in background daemon process
    try:
        backend_cmd = [
            sys.executable, "-m", "uvicorn",
            "backend.app:app",
            "--host", "127.0.0.1",
            "--port", "8000"
        ]
        subprocess.Popen(backend_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait up to 6 seconds for backend readiness
        for _ in range(30):
            try:
                with urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=0.5) as r:
                    if r.getcode() == 200:
                        break
            except Exception:
                time.sleep(0.2)
    except Exception as e:
        print(f"Notice: Background backend startup returned: {e}")

# Initialize backend for cloud environments (Streamlit Community Cloud, HF Spaces)
ensure_backend_running()

# Launch master UI
app_path = Path(__file__).resolve().parent / "aquora_ui" / "app.py"
runpy.run_path(str(app_path), run_name="__main__")
