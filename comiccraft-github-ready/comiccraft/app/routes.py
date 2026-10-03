"""HTTP routes: HTML pages, JSON API, PDF download and a diagnostic image test."""
import re
import traceback
from copy import deepcopy

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import ValidationError

from app.config import get_settings
from app.schemas import PromptRequest
from app.services.media import to_data_uri
from app.workflow import generate_comic

router = APIRouter()

_SAFE_PDF = re.compile(r"^comiccraft_[0-9_]+\.pdf$")


def _render(request: Request, name: str, context: dict, status_code: int = 200):
    return request.app.state.templates.TemplateResponse(request=request, name=name, context=context, status_code=status_code)


def _with_inline_images(result: dict) -> dict:
    """Embed every panel image as a data URI so the preview shows even if /static is misrouted."""
    context = deepcopy(result)
    for panel in context["layout"]:
        panel["image_src"] = to_data_uri(panel["image_path"]) or panel["image_path"]
    return context


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return _render(request, "index.html", {"error": None})


@router.post("/generate", response_class=HTMLResponse)
def generate_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        payload = PromptRequest(
            story_prompt=story_prompt.strip(),
            character_name=character_name.strip(),
            setting=setting.strip(),
            tone=tone.strip(),
            art_style=art_style.strip(),
        )
    except ValidationError:
        return _render(request, "index.html", {"error": "Please enter a story prompt of at least 5 characters and fill in every field."}, 422)
    try:
        result = generate_comic(payload)
        return _render(request, "comic_preview.html", _with_inline_images(result))
    except Exception as exc:  # noqa: BLE001
        traceback.print_exc()
        return _render(request, "index.html", {"error": str(exc)}, 500)


@router.post("/generate-comic/json")
def generate_json(payload: PromptRequest):
    try:
        return JSONResponse(content=generate_comic(payload))
    except Exception as exc:  # noqa: BLE001
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/download/{filename}")
def download_pdf(filename: str):
    if not _SAFE_PDF.match(filename):
        raise HTTPException(status_code=400, detail="Invalid file name.")
    path = get_settings().exports_dir / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(path, media_type="application/pdf", filename=filename)


@router.get("/export-success", response_class=HTMLResponse)
def export_success(request: Request, pdf_path: str = "", filename: str = ""):
    if not filename and pdf_path:
        filename = pdf_path.rsplit("/", 1)[-1]
    download_url = f"/download/{filename}" if _SAFE_PDF.match(filename or "") else ""
    return _render(request, "export_success.html", {"download_url": download_url})


@router.get("/test-image")
def test_image(prompt: str = "A futuristic city at sunset, sci-fi, cinematic, artstation"):
    """Developer utility: generate one image. Open the returned 'path' in your browser to view it."""
    from app.services.image_generator import ImageGenerationError, generate_image

    try:
        path = generate_image(prompt, 0)
        return {"message": "Image generated successfully", "path": path}
    except ImageGenerationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
