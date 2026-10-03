"""Pydantic models for requests and for the AI-generated comic content."""
from typing import List

from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    story_prompt: str = Field(min_length=5, max_length=2000)
    character_name: str = Field(min_length=1, max_length=80)
    setting: str = Field(min_length=1, max_length=120)
    tone: str = Field(min_length=1, max_length=80)
    art_style: str = Field(min_length=1, max_length=120)


class PanelOutline(BaseModel):
    panel_number: int = Field(default=1, ge=1)
    title: str = "Untitled"
    scene_description: str = ""
    image_prompt: str = ""


class ComicOutline(BaseModel):
    panels: List[PanelOutline]


class PanelStory(BaseModel):
    panel_number: int = Field(default=1, ge=1)
    title: str = "Untitled"
    scene_description: str = ""
    caption: str = ""
    narration: str = ""
    dialogue: str = ""
    image_prompt: str = ""


class ComicStory(BaseModel):
    panels: List[PanelStory]
