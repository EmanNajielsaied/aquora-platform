"""
Aquora Platform - Backend Service Launcher
Runs FastAPI backend on port 8000.
"""

import sys
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 STARTING AQUORA UNIFIED FASTAPI BACKEND SERVICE")
    print("=" * 60)
    print("📍 Host: http://0.0.0.0:8000")
    print("📖 Interactive API Docs: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/api/health")
    print("=" * 60)
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
