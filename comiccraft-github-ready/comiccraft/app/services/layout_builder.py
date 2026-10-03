"""Combine story text and image paths into one structure used by the preview page and the PDF."""
from typing import Dict, List

from app.schemas import ComicStory


def build_comic_layout(story: ComicStory, image_paths: List[str]) -> List[Dict]:
    if len(story.panels) != len(image_paths):
        raise ValueError("Every comic panel must have exactly one generated image.")
    layout = []
    for panel, image_path in zip(story.panels, image_paths):
        layout.append({
            "panel_number": panel.panel_number,
            "title": panel.title,
            "image_path": image_path,
            "scene_description": panel.scene_description,
            "caption": panel.caption,
            "narration": panel.narration,
            "dialogue": panel.dialogue,
            "image_prompt": panel.image_prompt,
        })
    return layout
