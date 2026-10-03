"""
ComicCraft image generation service.

Image generation order:

1. Hugging Face Spaces
2. Hugging Face Router (if configured)
3. Local Diffusers fallback

Images are saved to:
    static/panels/

The local Diffusers model is loaded lazily only when required.
This prevents FastAPI from crashing during application startup
when PyTorch/Diffusers are unavailable.
"""

import io
import re
import textwrap
import threading
import time
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont

from app.config import get_settings


# ============================================================
# Exceptions
# ============================================================

class ImageGenerationError(RuntimeError):
    """Raised when no configured image model can produce a usable image."""


# ============================================================
# State
# ============================================================

_PERMANENT_HINTS = (
    "404",
    "not found",
    "401",
    "403",
    "unauthorized",
    "forbidden",
    "gated",
    "not supported",
    "no provider",
    "not available",
    "invalid credentials",
    "invalid token",
    "402",
    "payment",
    "depleted",
    "quota",
    "credit",
)

_dead_models: Dict[str, float] = {}

_DEAD_SECONDS = 3600

_router_depleted: bool = False
_spaces_exhausted: bool = False

# Local Diffusers pipeline.
# IMPORTANT:
# It is NOT loaded during application startup.
_local_pipe = None

_local_lock = threading.Lock()


# ============================================================
# Utility functions
# ============================================================

def _safe_name(text: str) -> str:
    """Convert text into a safe filename."""

    value = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        text or "",
    ).strip("_")[:40]

    return value or "panel"


def _short(exc: Exception) -> str:
    """Return a short readable exception message."""

    return (
        " ".join(str(exc).split())[:200]
        or exc.__class__.__name__
    )


def _looks_blank(image: Image.Image) -> bool:
    """
    Detect nearly solid images.

    Some image services can return an almost completely
    black/blank image when generation fails.
    """

    low, high = image.convert("L").getextrema()

    return (high - low) < 3


# ============================================================
# Save generated image
# ============================================================

def _save_image(
    image: Image.Image,
    panel_number: int,
    label: str,
) -> str:
    """Save and verify a generated image."""

    settings = get_settings()

    settings.panels_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = (
        f"panel_{panel_number}_"
        f"{_safe_name(label)}_"
        f"{uuid4().hex[:8]}.jpg"
    )

    path = settings.panels_dir / filename

    # Always save RGB JPEG.
    image.convert("RGB").save(
        path,
        format="JPEG",
        quality=92,
    )

    # Verify file size.
    if path.stat().st_size < 1024:
        raise ImageGenerationError(
            "Saved image file is empty."
        )

    # Verify image integrity.
    try:
        with Image.open(path) as check:
            check.verify()
    except Exception as exc:
        raise ImageGenerationError(
            f"Generated image verification failed: {_short(exc)}"
        ) from exc

    return f"/static/panels/{filename}"


# ============================================================
# Local Diffusers model
# ============================================================

def preload_local_model():
    """
    Load the local Diffusers pipeline lazily.

    IMPORTANT:
    This function does NOT run automatically when FastAPI starts.

    PyTorch and Diffusers are imported only when local image
    generation is actually required.
    """

    global _local_pipe

    # Already loaded.
    if _local_pipe is not None:
        return _local_pipe

    # --------------------------------------------------------
    # Import heavy dependencies only when needed.
    # --------------------------------------------------------

    try:
        import torch

        from diffusers import (
            StableDiffusionPipeline,
            DiffusionPipeline,
            DPMSolverMultistepScheduler,
        )

    except ImportError as exc:

        raise ImageGenerationError(
            "Local image generation dependencies are missing. "
            "Install them with:\n"
            "pip install torch torchvision diffusers "
            "transformers accelerate safetensors"
        ) from exc

    settings = get_settings()

    # --------------------------------------------------------
    # Thread-safe model loading.
    # --------------------------------------------------------

    with _local_lock:

        # Another thread may have loaded it while we waited.
        if _local_pipe is not None:
            return _local_pipe

        model_id = (
            settings.local_image_model
            or "segmind/tiny-sd"
        )

        # ----------------------------------------------------
        # Detect GPU.
        # ----------------------------------------------------

        use_cuda = torch.cuda.is_available()

        if not use_cuda:
            try:
                torch.set_num_threads(6)
            except Exception:
                pass

        # ----------------------------------------------------
        # Load StableDiffusionPipeline.
        # If that fails, try generic DiffusionPipeline.
        # ----------------------------------------------------

        try:

            pipe = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=(
                    torch.float16
                    if use_cuda
                    else torch.float32
                ),
            )

        except Exception:

            try:

                pipe = DiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=(
                        torch.float16
                        if use_cuda
                        else torch.float32
                    ),
                )

            except Exception as exc:

                raise ImageGenerationError(
                    "Unable to load local Diffusers model "
                    f"'{model_id}': {_short(exc)}"
                ) from exc

        # ----------------------------------------------------
        # Try optimized scheduler.
        # ----------------------------------------------------

        try:

            pipe.scheduler = (
                DPMSolverMultistepScheduler.from_config(
                    pipe.scheduler.config
                )
            )

        except Exception:
            # Scheduler optimization is optional.
            pass

        # ----------------------------------------------------
        # Move pipeline to GPU/CPU.
        # ----------------------------------------------------

        try:

            pipe = pipe.to(
                "cuda"
                if use_cuda
                else "cpu"
            )

        except Exception as exc:

            raise ImageGenerationError(
                "Unable to move local image model to "
                f"{'CUDA' if use_cuda else 'CPU'}: "
                f"{_short(exc)}"
            ) from exc

        # ----------------------------------------------------
        # Disable progress bar.
        # ----------------------------------------------------

        try:
            pipe.set_progress_bar_config(
                disable=True
            )
        except Exception:
            pass

        _local_pipe = pipe

    return _local_pipe


# ============================================================
# Local image generation
# ============================================================

def _local_diffusers_image(
    prompt: str,
) -> Image.Image:
    """
    Generate an image using the local Diffusers model.

    The model is loaded only when this function is called.
    """

    global _local_pipe

    # Lazy loading.
    preload_local_model()

    settings = get_settings()

    size = settings.local_image_size or 512

    with _local_lock:

        if _local_pipe is None:
            raise ImageGenerationError(
                "Local image pipeline was not initialized."
            )

        try:

            result = _local_pipe(
                prompt,
                num_inference_steps=4,
                guidance_scale=5.5,
                width=size,
                height=size,
            )

        except Exception as exc:

            raise ImageGenerationError(
                f"Local Diffusers generation failed: "
                f"{_short(exc)}"
            ) from exc

    if not result.images:
        raise ImageGenerationError(
            "Local Diffusers returned no image."
        )

    return result.images[0].convert("RGB")


# ============================================================
# Hugging Face Spaces
# ============================================================

def _hf_space_image(
    prompt: str,
) -> Image.Image:
    """
    Generate an image using Hugging Face Spaces.

    Spaces are attempted before the paid Hugging Face Router.
    """

    import json
    import requests

    settings = get_settings()

    headers = {
        "User-Agent": "ComicCraft/2.0"
    }

    # --------------------------------------------------------
    # Free/remote Spaces.
    # --------------------------------------------------------

    spaces = [
        {
            "name": "FLUX.1-schnell",
            "url": (
                "https://black-forest-labs-flux-1-schnell.hf.space"
            ),
            "endpoint": "/gradio_api/call/infer",
            "data": [
                prompt,
                0,
                True,
                768,
                768,
                4,
            ],
        },
        {
            "name": "SD-3.5-Large-Turbo",
            "url": (
                "https://stabilityai-stable-diffusion-3-5-large-turbo.hf.space"
            ),
            "endpoint": "/gradio_api/call/infer",
            "data": [
                prompt,
                "",
                0,
                True,
                768,
                768,
                1.0,
                4,
            ],
        },
    ]

    errors: List[str] = []

    # --------------------------------------------------------
    # Try each Space.
    # --------------------------------------------------------

    for sp in spaces:

        try:

            base_url = sp["url"]
            endpoint = sp["endpoint"]

            # ------------------------------------------------
            # Start Gradio job.
            # ------------------------------------------------

            call_res = requests.post(
                f"{base_url}{endpoint}",
                json={
                    "data": sp["data"]
                },
                headers=headers,
                timeout=12,
            )

            if call_res.status_code != 200:

                errors.append(
                    f"{sp['name']}: "
                    f"HTTP {call_res.status_code}"
                )

                continue

            # ------------------------------------------------
            # Extract event ID.
            # ------------------------------------------------

            try:
                event_id = (
                    call_res.json()
                    .get("event_id")
                )
            except Exception:
                event_id = None

            if not event_id:

                errors.append(
                    f"{sp['name']}: no event_id"
                )

                continue

            # ------------------------------------------------
            # Stream result.
            # ------------------------------------------------

            stream_res = requests.get(
                f"{base_url}{endpoint}/{event_id}",
                headers=headers,
                stream=True,
                timeout=30,
            )

            img_url = None
            has_error = False

            for line in stream_res.iter_lines():

                if not line:
                    continue

                decoded = line.decode(
                    "utf-8",
                    errors="ignore",
                )

                # --------------------------------------------
                # Gradio error.
                # --------------------------------------------

                if "event: error" in decoded:

                    has_error = True
                    break

                # --------------------------------------------
                # Gradio data event.
                # --------------------------------------------

                if decoded.startswith("data:"):

                    try:

                        payload = json.loads(
                            decoded[5:].strip()
                        )

                        if (
                            isinstance(payload, list)
                            and len(payload) > 0
                        ):

                            item = payload[0]

                            if isinstance(item, dict):

                                # Direct URL.
                                if (
                                    item.get("url")
                                    and item["url"].startswith(
                                        "http"
                                    )
                                ):

                                    img_url = item["url"]
                                    break

                                # Gradio path.
                                elif item.get("path"):

                                    img_url = (
                                        f"{base_url}"
                                        f"/gradio_api/file="
                                        f"{item['path']}"
                                    )

                                    break

                                # Relative URL.
                                elif item.get("url"):

                                    img_url = (
                                        f"{base_url}"
                                        f"{item['url']}"
                                    )

                                    break

                    except Exception:
                        # Ignore malformed streaming events.
                        pass

            # ------------------------------------------------
            # No image received.
            # ------------------------------------------------

            if has_error or not img_url:

                errors.append(
                    f"{sp['name']}: "
                    "queue/quota unavailable"
                )

                continue

            # ------------------------------------------------
            # Download image.
            # ------------------------------------------------

            img_res = requests.get(
                img_url,
                headers=headers,
                timeout=20,
            )

            if (
                img_res.status_code != 200
                or len(img_res.content) < 1024
            ):

                errors.append(
                    f"{sp['name']}: download failed"
                )

                continue

            # ------------------------------------------------
            # Open downloaded image.
            # ------------------------------------------------

            img = Image.open(
                io.BytesIO(img_res.content)
            )

            return img.convert("RGB")

        except Exception as exc:

            errors.append(
                f"{sp['name']}: {_short(exc)}"
            )

    raise ImageGenerationError(
        "Spaces generation unavailable: "
        + " | ".join(errors)
    )


# ============================================================
# Hugging Face Router
# ============================================================

def _huggingface_router_image(
    prompt: str,
    model: str,
) -> Image.Image:
    """Generate image using the Hugging Face inference router."""

    global _router_depleted

    # --------------------------------------------------------
    # Never retry router after HTTP 402.
    # --------------------------------------------------------

    if _router_depleted:

        raise ImageGenerationError(
            "Hugging Face router credits depleted "
            "(HTTP 402); skipping paid endpoints."
        )

    # --------------------------------------------------------
    # Import only when router is actually used.
    # --------------------------------------------------------

    try:

        from huggingface_hub import InferenceClient

    except ImportError as exc:

        raise ImageGenerationError(
            "huggingface_hub is not installed. "
            "Install it with: "
            "pip install huggingface_hub"
        ) from exc

    settings = get_settings()

    client = InferenceClient(
        provider=(
            settings.image_provider
            or "auto"
        ),
        api_key=settings.hf_token,
        timeout=min(
            settings.image_timeout,
            45,
        ),
    )

    try:

        # ----------------------------------------------------
        # First attempt with configured dimensions.
        # ----------------------------------------------------

        result = client.text_to_image(
            prompt,
            model=model,
            width=settings.image_width,
            height=settings.image_height,
        )

    except Exception as exc:

        msg = str(exc).lower()

        # ----------------------------------------------------
        # HTTP 402 / payment / credits.
        # ----------------------------------------------------

        if any(
            k in msg
            for k in (
                "402",
                "payment",
                "depleted",
                "credit",
            )
        ):

            _router_depleted = True

            raise ImageGenerationError(
                "Hugging Face monthly credits "
                "depleted (HTTP 402)."
            ) from exc

        # ----------------------------------------------------
        # Retry without width/height for unsupported models.
        # ----------------------------------------------------

        if any(
            k in msg
            for k in (
                "width",
                "height",
                "size",
                "parameter",
                "422",
                "400",
            )
        ):

            try:

                result = client.text_to_image(
                    prompt,
                    model=model,
                )

            except Exception as retry_exc:

                if any(
                    k in str(retry_exc).lower()
                    for k in (
                        "402",
                        "payment",
                        "depleted",
                        "credit",
                    )
                ):

                    _router_depleted = True

                    raise ImageGenerationError(
                        "Hugging Face monthly credits "
                        "depleted (HTTP 402)."
                    ) from retry_exc

                raise

        else:

            raise

    # --------------------------------------------------------
    # Convert byte response to PIL image.
    # --------------------------------------------------------

    if isinstance(
        result,
        (bytes, bytearray),
    ):

        result = Image.open(
            io.BytesIO(result)
        )

    # --------------------------------------------------------
    # Validate result.
    # --------------------------------------------------------

    if not isinstance(
        result,
        Image.Image,
    ):

        raise ImageGenerationError(
            "Unexpected response type from image API: "
            f"{type(result).__name__}"
        )

    return result.convert("RGB")


# ============================================================
# Public image generation API
# ============================================================

def generate_image(
    prompt: str,
    panel_number: int = 0,
    art_style: str = "",
) -> str:
    """
    Generate one comic panel image.

    Backend order:

    local
        -> Local Diffusers

    spaces
        -> Hugging Face Spaces

    huggingface/router
        -> Hugging Face Router

    auto
        -> Spaces
        -> Router
        -> Local Diffusers
    """

    global _router_depleted
    global _spaces_exhausted

    settings = get_settings()

    # --------------------------------------------------------
    # Build comic prompt.
    # --------------------------------------------------------

    if art_style:

        style = (
            f"{art_style} style comic panel. "
        )

    else:

        style = "Comic panel. "

    full_prompt = (
        f"{style}"
        f"{prompt}. "
        "Clear composition, expressive characters, "
        "vivid colors, no text, no speech bubbles, "
        "no watermark."
    )

    backend = (
        settings.image_backend
        or "auto"
    ).lower()

    errors: List[str] = []

    # ========================================================
    # 1. Direct local Diffusers
    # ========================================================

    if backend == "local":

        try:

            image = _local_diffusers_image(
                full_prompt
            )

            if not _looks_blank(image):

                return _save_image(
                    image,
                    panel_number,
                    prompt,
                )

        except Exception as exc:

            errors.append(
                "Local diffusers failed: "
                f"{_short(exc)}"
            )

    # ========================================================
    # 2. Hugging Face Spaces
    # ========================================================

    if (
        not _spaces_exhausted
        and backend in (
            "auto",
            "spaces",
            "hybrid",
            "cloud",
        )
    ):

        try:

            image = _hf_space_image(
                full_prompt
            )

            if not _looks_blank(image):

                return _save_image(
                    image,
                    panel_number,
                    prompt,
                )

        except Exception as exc:

            _spaces_exhausted = True

            errors.append(
                "HF Spaces: "
                f"{_short(exc)}"
            )

    # ========================================================
    # 3. Hugging Face Router
    # ========================================================

    if (
        settings.hf_token
        and not _router_depleted
        and backend in (
            "auto",
            "huggingface",
            "router",
        )
    ):

        models = [
            model
            for model in settings.image_models
            if (
                time.time()
                - _dead_models.get(model, 0)
                > _DEAD_SECONDS
            )
        ]

        for model in models:

            try:

                image = _huggingface_router_image(
                    full_prompt,
                    model,
                )

                if not _looks_blank(image):

                    return _save_image(
                        image,
                        panel_number,
                        prompt,
                    )

            except Exception as exc:

                msg = _short(exc)

                errors.append(
                    f"{model}: {msg}"
                )

                # ------------------------------------------------
                # Permanently unavailable model.
                # ------------------------------------------------

                if any(
                    hint in msg.lower()
                    for hint in _PERMANENT_HINTS
                ):

                    _dead_models[model] = (
                        time.time()
                    )

                if _router_depleted:
                    break

    # ========================================================
    # 4. Local Diffusers fallback
    # ========================================================

    try:

        image = _local_diffusers_image(
            full_prompt
        )

        if not _looks_blank(image):

            return _save_image(
                image,
                panel_number,
                prompt,
            )

    except Exception as local_exc:

        errors.append(
            "Local fallback failed: "
            f"{_short(local_exc)}"
        )

    # ========================================================
    # Everything failed.
    # ========================================================

    raise ImageGenerationError(
        "All image generation providers exhausted: "
        + " | ".join(errors)
    )


# ============================================================
# Placeholder image
# ============================================================

def create_placeholder_image(
    panel_number: int,
    title: str,
    style: str = "",
    note: str = "",
) -> str:
    """
    Create a fallback graphic when real image generation
    temporarily fails and placeholders are enabled.
    """

    settings = get_settings()

    size = 512

    bg_color = (
        20,
        24,
        38,
    )

    image = Image.new(
        "RGB",
        (size, size),
        bg_color,
    )

    draw = ImageDraw.Draw(image)

    # --------------------------------------------------------
    # Border.
    # --------------------------------------------------------

    draw.rectangle(
        (
            12,
            12,
            size - 12,
            size - 12,
        ),
        outline=(
            60,
            75,
            110,
        ),
        width=3,
    )

    draw.rectangle(
        (
            18,
            18,
            size - 18,
            size - 18,
        ),
        outline=(
            130,
            90,
            220,
        ),
        width=4,
    )

    # --------------------------------------------------------
    # Fonts.
    # --------------------------------------------------------

    try:

        big = ImageFont.load_default(
            size=32
        )

        mid = ImageFont.load_default(
            size=20
        )

        small = ImageFont.load_default(
            size=16
        )

    except TypeError:

        # Compatibility with older Pillow versions.
        big = ImageFont.load_default()
        mid = ImageFont.load_default()
        small = ImageFont.load_default()

    # --------------------------------------------------------
    # Panel label.
    # --------------------------------------------------------

    draw.rectangle(
        (
            36,
            36,
            200,
            80,
        ),
        fill=(
            130,
            90,
            220,
        ),
    )

    draw.text(
        (
            48,
            44,
        ),
        f"PANEL {panel_number}",
        fill=(
            255,
            255,
            255,
        ),
        font=big,
    )

    # --------------------------------------------------------
    # Scene.
    # --------------------------------------------------------

    y = 110

    draw.text(
        (
            40,
            y,
        ),
        "SCENE:",
        fill=(
            140,
            160,
            200,
        ),
        font=small,
    )

    y += 26

    for line in textwrap.wrap(
        title or "Graphic Action Sequence",
        width=30,
    )[:3]:

        draw.text(
            (
                40,
                y,
            ),
            line,
            fill=(
                245,
                245,
                255,
            ),
            font=mid,
        )

        y += 28

    # --------------------------------------------------------
    # Art style.
    # --------------------------------------------------------

    if style:

        y += 16

        draw.text(
            (
                40,
                y,
            ),
            f"Art Style: {style}",
            fill=(
                210,
                180,
                80,
            ),
            font=small,
        )

        y += 24

    # --------------------------------------------------------
    # Comic visual area.
    # --------------------------------------------------------

    draw.rectangle(
        (
            40,
            y + 10,
            size - 40,
            size - 50,
        ),
        outline=(
            45,
            55,
            80,
        ),
        width=2,
        fill=(
            14,
            17,
            27,
        ),
    )

    draw.text(
        (
            size // 2 - 90,
            (
                y
                + 10
                + size
                - 50
            )
            // 2
            - 10,
        ),
        "[ COMIC SCENE VISUAL ]",
        fill=(
            100,
            120,
            160,
        ),
        font=mid,
    )

    # --------------------------------------------------------
    # Save placeholder.
    # --------------------------------------------------------

    settings.panels_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = (
        f"placeholder_{panel_number}_"
        f"{uuid4().hex[:8]}.jpg"
    )

    path = (
        settings.panels_dir
        / filename
    )

    image.save(
        path,
        format="JPEG",
        quality=92,
    )

    return f"/static/panels/{filename}"


# ============================================================
# Safe image generation
# ============================================================

def generate_image_safe(
    prompt: str,
    panel_number: int,
    title: str = "",
    art_style: str = "",
) -> Tuple[str, Optional[str]]:
    """
    Safe wrapper around generate_image().

    If placeholder_on_failure is enabled,
    the application returns a placeholder instead of
    crashing the request.
    """

    settings = get_settings()

    try:

        return (
            generate_image(
                prompt,
                panel_number,
                art_style,
            ),
            None,
        )

    except ImageGenerationError as exc:

        if not settings.placeholder_on_failure:
            raise

        reason = str(exc)

        # ----------------------------------------------------
        # Never expose raw provider errors to users.
        # ----------------------------------------------------

        if any(
            k in reason.lower()
            for k in (
                "402",
                "depleted",
                "payment",
                "credit",
                "zerogpu",
                "quota",
            )
        ):

            short_warn = (
                f"Panel {panel_number}: "
                "Cloud GPU quota cooling down. "
                "Fallback panel created."
            )

        else:

            short_warn = (
                f"Panel {panel_number}: "
                "Image generation completed "
                "with local backup."
            )

        url = create_placeholder_image(
            panel_number,
            title,
            art_style,
            note="",
        )

        return (
            url,
            short_warn,
        )