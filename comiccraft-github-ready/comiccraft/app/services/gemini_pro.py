"""Gemini Pro: narration, captions and dialogue for every panel."""
from app.config import get_settings
from app.schemas import ComicOutline, ComicStory, PanelStory
from app.services.llm_utils import call_with_model_fallback, extract_json, generate_text, panels_from_json

PANEL_COUNT = 5


def generate_story(outline: ComicOutline, story_prompt: str, character_name: str, tone: str) -> ComicStory:
    settings = get_settings()
    prompt = f"""You are a comic book writer. Expand this {PANEL_COUNT}-panel outline into polished comic narration and dialogue.

Original idea: {story_prompt}
Main character: {character_name}
Tone: {tone}

Outline (JSON):
{outline.model_dump_json(indent=2)}

For every panel keep its panel_number, title, scene_description and image_prompt unchanged, and add:
- "caption": one short ambient caption (environment or sound)
- "narration": 1-2 sentences of narration
- "dialogue": natural character dialogue with the speaker named, e.g. {character_name}: "..."
Keep the story continuous and suitable for a general audience.

Respond ONLY with valid JSON (no markdown) in exactly this shape:
{{"panels": [{{"panel_number": 1, "title": "...", "scene_description": "...", "caption": "...", "narration": "...", "dialogue": "...", "image_prompt": "..."}}]}}
Return exactly {PANEL_COUNT} panels."""

    def run(client, model: str) -> ComicStory:
        raw = generate_text(client, model, prompt, temperature=0.85)
        items = panels_from_json(extract_json(raw))
        panels = []
        for index, item in enumerate(items[:PANEL_COUNT], start=1):
            item = dict(item)
            item["panel_number"] = index
            source = outline.panels[index - 1] if index <= len(outline.panels) else None
            # Always keep the outline's image prompt / title if the model dropped them.
            if source:
                item.setdefault("title", source.title)
                if not str(item.get("image_prompt", "")).strip():
                    item["image_prompt"] = source.image_prompt
                if not str(item.get("scene_description", "")).strip():
                    item["scene_description"] = source.scene_description
            for key in ("caption", "narration", "dialogue"):
                value = item.get(key, "")
                if isinstance(value, list):  # some models return dialogue as a list of lines
                    item[key] = "\n".join(str(v) for v in value)
                elif not isinstance(value, str):
                    item[key] = str(value)
            panels.append(PanelStory.model_validate(item))
        if len(panels) != PANEL_COUNT:
            raise ValueError(f"Expected {PANEL_COUNT} panels but received {len(panels)}.")
        return ComicStory(panels=panels)

    return call_with_model_fallback(settings.story_models, run)
