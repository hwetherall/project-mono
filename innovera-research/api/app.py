"""
FastAPI application - CORS, static mount, route registration.
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import router as api_router
from api.websocket import router as ws_router

app = FastAPI(title="Innovera Research", version="1.0.0")

# CORS for Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(api_router)
app.include_router(ws_router)


@app.on_event("startup")
async def startup():
    """Ensure required directories exist and mount frontend if built."""
    from config.settings import OUTPUT_DIR, VENTURE_DOCS_DIR
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    VENTURE_DOCS_DIR.mkdir(parents=True, exist_ok=True)


# Serve frontend static files (AFTER API routes)
_frontend_dir = Path(__file__).parent.parent / "frontend" / "dist"
if _frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dir), html=True), name="frontend")
