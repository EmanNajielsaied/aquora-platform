"""
Aquora Platform - Production Multi-Process Supervisor
Launches both the FastAPI backend and Streamlit frontend in a unified environment.
Ideal for single-container or unified cloud instances (e.g. Render single service, Koyeb, Docker).
"""

import os
import sys
import time
import subprocess
import signal
import urllib.request
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("aquora.supervisor")

def main():
    public_port = int(os.environ.get("PORT", os.environ.get("APP_PORT", 7860)))
    internal_api_port = int(os.environ.get("API_PORT", 8000))
    host = "0.0.0.0"

    logger.info("Starting Aquora Production Services...")
    logger.info(f"Internal API Port: {internal_api_port} | Public UI Port: {public_port}")

    # 1. Start FastAPI Backend
    api_cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.app:app",
        "--host", "127.0.0.1",
        "--port", str(internal_api_port)
    ]
    logger.info(f"Launching FastAPI backend: {' '.join(api_cmd)}")
    api_proc = subprocess.Popen(api_cmd)

    # 2. Health Wait
    logger.info("Waiting for FastAPI backend to initialize...")
    for _ in range(30):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{internal_api_port}/api/health", timeout=1) as resp:
                if resp.getcode() == 200:
                    logger.info("FastAPI backend is READY and ONLINE.")
                    break
        except Exception:
            time.sleep(0.5)
    else:
        logger.warning("Backend did not respond within timeout, proceeding with Streamlit launch anyway.")

    # 3. Start Streamlit Frontend
    env = os.environ.copy()
    env["AQUORA_API_URL"] = f"http://127.0.0.1:{internal_api_port}"

    ui_cmd = [
        sys.executable, "-m", "streamlit", "run",
        "aquora_ui/app.py",
        "--server.port", str(public_port),
        "--server.address", host,
        "--server.headless", "true",
        "--theme.base", "dark",
        "--theme.primaryColor", "#0ea5e9",
        "--theme.backgroundColor", "#070b14",
        "--theme.secondaryBackgroundColor", "#0f172a",
        "--theme.textColor", "#f8fafc"
    ]
    logger.info(f"Launching Streamlit frontend: {' '.join(ui_cmd)}")
    ui_proc = subprocess.Popen(ui_cmd, env=env)

    # Graceful shutdown handler
    def shutdown(sig, frame):
        logger.info("Shutting down processes...")
        ui_proc.terminate()
        api_proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Monitor processes
    while True:
        if api_proc.poll() is not None:
            logger.error("FastAPI process exited unexpectedly!")
            ui_proc.terminate()
            sys.exit(api_proc.returncode or 1)
        if ui_proc.poll() is not None:
            logger.info("Streamlit process stopped.")
            api_proc.terminate()
            sys.exit(ui_proc.returncode or 0)
        time.sleep(1)

if __name__ == "__main__":
    main()
