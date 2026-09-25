"""
Easeprompt FastAPI Server.
Provides high-performance SSE streaming, prompt analysis, preset templates,
and serves the modern cybernetic dark-mode web application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .models import (
    ExpandPromptRequest,
    ExplainPromptRequest,
    ExplanationData,
    TestPromptRequest,
    TestPromptResponse
)
from .expansion_engine import ExpansionEngine
from .rate_limiter import RateLimitMiddleware

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Easeprompt",
    description="Principal Prompt Engineering & Meta-Prompt Expansion Engine",
    version="1.0.0"
)

# Rate limiting middleware for production bot protection (30 requests/min per IP)
app.add_middleware(RateLimitMiddleware, limit=30, window_seconds=60)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = ExpansionEngine()

# Resolve static directory path
STATIC_DIR = Path(__file__).parent / "static"


@app.get("/health")
async def health_check():
    """Production health check endpoint for monitoring & load balancers."""
    return {"status": "healthy", "service": "easeprompt", "version": "1.0.0"}


@app.get("/")
async def root():
    """Serves the primary UI application."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="UI index.html not found")
    return FileResponse(index_file)


@app.post("/api/expand-stream")
async def expand_prompt_stream(request: ExpandPromptRequest):
    """
    Server-Sent Events (SSE) streaming endpoint.
    Streams token-by-token expansion in real time without lag.
    """
    if not request.input_text or not request.input_text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    return StreamingResponse(
        engine.stream_expansion(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/explain", response_model=ExplanationData)
async def explain_prompt(request: ExplainPromptRequest):
    """
    Returns an architectural deconstruction of the prompt:
    detected intent, extrapolated technical context, negative constraints, and dynamic placeholders.
    """
    return engine.explain_prompt(
        input_text=request.input_text,
        target_agent=request.target_agent,
        framework_style=request.framework_style,
        generated_prompt=request.generated_prompt
    )


@app.post("/api/test-prompt", response_model=TestPromptResponse)
async def test_prompt(request: TestPromptRequest):
    """
    Populates placeholders with user parameters and provides execution simulation.
    """
    result = engine.test_run_prompt(
        prompt_text=request.prompt_text,
        variables=request.variables
    )
    return TestPromptResponse(**result)


@app.get("/api/presets")
async def get_presets():
    """
    Returns high-yield industry presets for one-click testing.
    """
    return [
        {
            "title": "Crypto Live Tracker",
            "input": "crypto tracker",
            "target": "coding_assistant",
            "framework": "art_framework",
            "badge": "Web3 / Real-time"
        },
        {
            "title": "Customer Churn Predictor",
            "input": "I want to analyze customer churn",
            "target": "data_analyst",
            "framework": "art_framework",
            "badge": "ML / Analytics"
        },
        {
            "title": "Microservice OAuth2 Flow",
            "input": "microservice authentication with jwt and rbac",
            "target": "security_auditor",
            "framework": "modular_spec",
            "badge": "AppSec / Cloud"
        },
        {
            "title": "Postgres Query Tuning",
            "input": "optimize slow postgres queries with indexes",
            "target": "system_architect",
            "framework": "modular_spec",
            "badge": "Database / High-Load"
        },
        {
            "title": "Autonomous Web Scraper",
            "input": "autonomous price intelligence scraper with rate limits",
            "target": "autonomous_agent",
            "framework": "autonomous_react",
            "badge": "ReAct Agent"
        },
        {
            "title": "Sci-Fi Cyberpunk Lorebook",
            "input": "cyberpunk megacity lorebook and character bios",
            "target": "creative_writer",
            "framework": "art_framework",
            "badge": "Creative"
        }
    ]


@app.get("/api/config")
async def get_system_config():
    """
    Returns server capabilities, detected keys, and default provider.
    """
    return {
        "default_provider": engine.default_provider,
        "providers_available": {
            "builtin": True,
            "gemini": bool(engine.gemini_key),
            "openai": bool(engine.openai_key),
            "groq": bool(engine.groq_key),
            "ollama": True
        }
    }


# Mount static assets (CSS, JS, fonts)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    print(f"\n[Easeprompt] launching at http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)

