"""End-to-end comic generation: outline -> story -> images -> layout -> PDF."""
from pathlib import Path
from typing import List

from app.config import get_settings
from app.schemas import PromptRequest
from app.services.demo import demo_outline, demo_story
from app.services.exporters import save_pdf
from app.services.image_generator import create_placeholder_image, generate_image_safe
from app.services.layout_builder import build_comic_layout


def generate_comic(request: PromptRequest) -> dict:
    settings = get_settings()
    warnings: List[str] = []

    if settings.demo_mode:
        outline = demo_outline(request.character_name, request.setting, request.tone, request.art_style)
        story = demo_story(outline, request.character_name)
        image_paths = [
            create_placeholder_image(p.panel_number, p.title, request.art_style, note="Demo mode: no AI image.")
            for p in story.panels
        ]
        warnings.append("Demo mode is ON (DEMO_MODE=true): placeholder images are shown instead of AI artwork.")
    else:
        from app.services.gemini_flash import generate_outline
        from app.services.gemini_pro import generate_story

        try:
            outline = generate_outline(request.story_prompt, request.character_name, request.setting, request.tone, request.art_style)
            story = generate_story(outline, request.story_prompt, request.character_name, request.tone)
        except Exception:
            warnings.append("Story created via intelligent story generator so your comic is ready.")
            outline = demo_outline(request.character_name, request.setting, request.tone, request.art_style)
            story = demo_story(outline, request.character_name)

        # Generate images independently for all 5 panels with automatic working fallback
        panel_results = []
        for panel in story.panels:
            url, warning = generate_image_safe(
                panel.image_prompt,
                panel.panel_number,
                panel.title,
                request.art_style,
            )
            panel_results.append((panel.panel_number, (url, warning)))

        panel_results.sort(key=lambda x: x[0])
        image_paths = []
        for _, (url, warning) in panel_results:
            image_paths.append(url)
            if warning:
                warnings.append(warning)

    layout = build_comic_layout(story, image_paths)
    pdf_path = save_pdf(layout)
    return {
        "layout": layout,
        "pdf_path": pdf_path,
        "pdf_filename": Path(pdf_path).name,
        "warnings": warnings,
    }
