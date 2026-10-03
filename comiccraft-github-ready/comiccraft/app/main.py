"""FastAPI application entry point:  uvicorn app.main:app --reload"""
import sys
from pathlib import Path

# Ensure project root and app directory are in sys.path so 'app' can always be imported
_app_dir = Path(__file__).resolve().parent
_project_root = _app_dir.parent
for _p in (r"C:\RASH\comiccraft", str(_project_root), str(_app_dir)):
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.routes import router

settings = get_settings()

# StaticFiles raises an error if the folder is missing, so create everything up front.
for folder in (settings.static_dir, settings.panels_dir, settings.exports_dir):
    folder.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.app_name,
    version="1.1.0",
    description="AI Comic Story Creator using Gemini and Stable Diffusion / FLUX",
)
app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
app.state.templates = Jinja2Templates(directory=str(settings.templates_dir))
app.include_router(router)


@app.on_event("startup")
def on_startup():
    if settings.image_backend.lower() == "local":
        from app.services.image_generator import preload_local_model
        preload_local_model()


@app.get("/health")
def health():
    """Quick configuration check (never exposes the keys themselves)."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "demo_mode": settings.demo_mode,
        "gemini_key_set": bool(settings.gemini_api_key),
        "hf_token_set": bool(settings.hf_token),
        "image_backend": settings.image_backend,
        "image_models": settings.image_models if settings.image_backend.lower() != "local" else [settings.local_image_model],
        "outline_models": settings.outline_models,
        "story_models": settings.story_models,
        "panels_dir": str(settings.panels_dir),
        "panels_dir_exists": settings.panels_dir.is_dir(),
    }
