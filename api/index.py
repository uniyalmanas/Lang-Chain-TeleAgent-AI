import os
import sys

# Ensure root workspace directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from backend.main import app
except Exception as e:
    print(f"[VERCEL IMPORT ERROR] {e}")
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    def fallback_handler(path: str):
        return {
            "status": "fallback",
            "message": f"TeleAgent AI Serverless Engine fallback active. Error details: {str(e)}"
        }
