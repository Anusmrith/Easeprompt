"""
Easeprompt Root Entrypoint.
Run directly with:
    python main.py
Or with uvicorn:
    uvicorn main:app --reload --port 8000
"""

import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    print("=======================================================")
    print("  [Easeprompt] Meta-Prompt Expansion Engine")
    print(f"  Running locally: http://{host}:{port}")
    print("  Open your browser to access the Easeprompt UI")
    print("=======================================================\n")
    uvicorn.run("main:app", host=host, port=port, reload=True)

