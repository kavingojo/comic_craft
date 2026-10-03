"""Gemini Flash: fast, structured 5-panel comic outline."""
from app.config import get_settings
from app.schemas import ComicOutline, PanelOutline
from app.services.llm_utils import call_with_model_fallback, extract_json, generate_text, panels_from_json

PANEL_COUNT = 5


def generate_outline(story_prompt: str, character_name: str, setting: str, tone: str, art_style: str) -> ComicOutline:
    settings = get_settings()
    prompt = f"""You are a professional comic planner. Create exactly {PANEL_COUNT} connected comic panels.

Story idea: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

The story needs a beginning, development, conflict, climax and ending.
Keep the main character visually consistent: describe their look the same way in every image_prompt.

Respond ONLY with valid JSON (no markdown, no explanations) in exactly this shape:
{{"panels": [
  {{"panel_number": 1, "title": "Short title", "scene_description": "What happens in this panel", "image_prompt": "Detailed visual prompt for an image generator, in {art_style} style, no text in the image"}}
]}}"""

    def run(client, model: str) -> ComicOutline:
        raw = generate_text(client, model, prompt, temperature=0.9)
        items = panels_from_json(extract_json(raw))
        panels = []
        for index, item in enumerate(items[:PANEL_COUNT], start=1):
            item = dict(item)
            item["panel_number"] = index
            panel = PanelOutline.model_validate(item)
            if not panel.image_prompt.strip():
                panel.image_prompt = f"{art_style} illustration of {character_name} in {setting}: {panel.scene_description}"
            panels.append(panel)
        if len(panels) != PANEL_COUNT:
            raise ValueError(f"Expected {PANEL_COUNT} panels but received {len(panels)}.")
        return ComicOutline(panels=panels)

    return call_with_model_fallback(settings.outline_models, run)
