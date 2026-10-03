"""Application settings, loaded from environment variables / the .env file."""
import os
from functools import lru_cache
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_base_dir() -> Path:
    """Find the project base directory where static/ and templates/ live."""
    parent = Path(__file__).resolve().parent.parent
    if (parent / "templates").is_dir() or (parent / "static").is_dir():
        return parent
    cwd = Path.cwd()
    if (cwd / "templates").is_dir() or (cwd / "static").is_dir():
        return cwd
    candidate = Path(r"C:\RASH\comiccraft")
    if (candidate / "templates").is_dir():
        return candidate
    return parent


BASE_DIR = _resolve_base_dir()

# Discover and load .env files into os.environ
_CANDIDATE_ENV_DIRS = [
    Path(__file__).resolve().parent.parent,
    Path.cwd(),
    Path(__file__).resolve().parent,
    Path(r"C:\RASH\comiccraft"),
]
_ENV_FILES: List[str] = []
for _dir in _CANDIDATE_ENV_DIRS:
    _env_path = _dir / ".env"
    if _env_path.is_file() and str(_env_path) not in _ENV_FILES:
        _ENV_FILES.append(str(_env_path))
        load_dotenv(dotenv_path=_env_path, override=False)


def _split(value: str) -> List[str]:
    return [item.strip() for item in (value or "").split(",") if item.strip()]


class Settings(BaseSettings):
    app_name: str = "ComicCraft"

    # ---- Gemini (text) -------------------------------------------------
    gemini_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GEMINI_API_KEY", "gemini_api_key", "GOOGLE_API_KEY"),
    )
    # Comma-separated lists: the first model that works is used.
    gemini_model_outline: str = "gemini-3.1-flash-lite,gemini-3.5-flash-lite,gemini-3.6-flash,gemini-3-flash-preview,gemini-3.8-flash,gemini-flash-latest"
    gemini_model_story: str = "gemini-3.1-flash-lite,gemini-3.5-flash-lite,gemini-3.6-flash,gemini-3-flash-preview,gemini-3.8-flash,gemini-flash-latest"

    # ---- Images --------------------------------------------------------
    # Accepts HF_TOKEN (preferred) or HF_API_KEY (name used in the project document).
    hf_token: str = Field(
        default="",
        validation_alias=AliasChoices("HF_TOKEN", "hf_token", "HF_API_KEY", "HUGGINGFACE_API_KEY"),
    )
    image_backend: str = "local"  # "local" (diffusers, 100% free & offline, no 402 errors), "spaces", or "huggingface"
    image_model: str = "segmind/tiny-sd"
    image_fallback_models: str = "segmind/tiny-sd"
    image_provider: str = "auto"
    image_width: int = 768
    image_height: int = 768
    image_steps: int = 6
    image_timeout: int = 60
    local_image_model: str = "segmind/tiny-sd"
    local_image_size: int = 512

    # If every image model fails, show a labelled placeholder instead of a broken image.
    placeholder_on_failure: bool = True
    demo_mode: bool = False
    secret_key: str = "change-me-in-production"

    model_config = SettingsConfigDict(
        env_file=tuple(_ENV_FILES) if _ENV_FILES else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @field_validator("gemini_api_key", "hf_token", mode="before")
    @classmethod
    def _clean_key(cls, value):
        """Treat blanks and the untouched .env.example placeholders as 'not set'."""
        value = (value or "").strip().strip('"').strip("'")
        return "" if value.lower().startswith("your_") else value

    @property
    def outline_models(self) -> List[str]:
        return _split(self.gemini_model_outline)

    @property
    def story_models(self) -> List[str]:
        return _split(self.gemini_model_story)

    @property
    def image_models(self) -> List[str]:
        models = [self.image_model.strip()] + _split(self.image_fallback_models)
        seen, ordered = set(), []
        for m in models:
            if m and m not in seen:
                seen.add(m)
                ordered.append(m)
        return ordered

    @property
    def static_dir(self) -> Path:
        return BASE_DIR / "static"

    @property
    def panels_dir(self) -> Path:
        return self.static_dir / "panels"

    @property
    def exports_dir(self) -> Path:
        return self.static_dir / "exports"

    @property
    def templates_dir(self) -> Path:
        return BASE_DIR / "templates"


@lru_cache
def get_settings() -> Settings:
    return Settings()
