"""Helpers for turning /static/... URLs into files and inline data URIs."""
import base64
import mimetypes
from pathlib import Path
from typing import Optional

from app.config import get_settings


def local_path_from_url(url_path: str) -> Optional[Path]:
    """Map '/static/panels/x.jpg' to an absolute file path inside the static folder."""
    if not url_path or not url_path.startswith("/static/"):
        return None
    static_dir = get_settings().static_dir.resolve()
    candidate = (static_dir / url_path[len("/static/"):]).resolve()
    try:
        candidate.relative_to(static_dir)  # blocks ../ path traversal
    except ValueError:
        return None
    return candidate


def to_data_uri(url_path: str) -> str:
    """Return the image as a base64 data URI so the browser never needs a second request."""
    path = local_path_from_url(url_path)
    if not path or not path.is_file():
        return ""
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")
