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
    is_prod = bool(os.getenv("PORT") or os.getenv("RENDER") or os.getenv("RAILWAY_ENVIRONMENT"))
    default_host = "0.0.0.0" if is_prod else "127.0.0.1"
    host = os.getenv("HOST", default_host)
    port = int(os.getenv("PORT", 8000))
    reload = not is_prod

    print("=======================================================")
    print("  [Easeprompt] Meta-Prompt Expansion Engine")
    print(f"  Running on: http://{host}:{port}")
    print(f"  Mode: {'Production' if is_prod else 'Development (Reload Enabled)'}")
    print("=======================================================\n")
    uvicorn.run("main:app", host=host, port=port, reload=reload)

