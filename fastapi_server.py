"""
Standalone HTTP API server for receipt-parser.
DEPRECATED: This file is kept for backward compatibility only.
All functionality has been moved to src.adapters.api.fastapi_app

Run with:
    uvicorn fastapi_server:app --reload --port 8001
    or (recommended):
    uvicorn src.adapters.api.fastapi_app:app --reload --port 8001
"""
import sys
import os

from dotenv import load_dotenv
load_dotenv()

# Add src to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from src.adapters.api.fastapi_app import app

__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

