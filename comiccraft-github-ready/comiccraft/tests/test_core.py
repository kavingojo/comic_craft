import pytest

from app.schemas import ComicStory, PanelStory, PromptRequest
from app.services.exporters import _pdf_text
from app.services.layout_builder import build_comic_layout
from app.services.llm_utils import extract_json, panels_from_json


def _story():
    return ComicStory(panels=[
        PanelStory(panel_number=i, title=f"P{i}", scene_description="scene", caption="caption",
                   narration="narration", dialogue="dialogue", image_prompt="prompt")
        for i in range(1, 6)
    ])


def test_prompt_request_validation():
    item = PromptRequest(story_prompt="A fox adventure", character_name="Finn", setting="Forest", tone="Funny", art_style="Anime")
    assert item.character_name == "Finn"


def test_layout_matches_images():
    layout = build_comic_layout(_story(), [f"/static/panels/{i}.jpg" for i in range(1, 6)])
    assert len(layout) == 5
    assert layout[0]["image_path"].endswith("1.jpg")


def test_layout_rejects_missing_images():
    with pytest.raises(ValueError):
        build_comic_layout(_story(), ["/static/panels/1.jpg"])


def test_extract_json_handles_code_fences_and_prose():
    assert extract_json('```json\n{"panels": []}\n```') == {"panels": []}
    assert extract_json('Sure! Here it is: {"a": 1} hope that helps') == {"a": 1}
    with pytest.raises(ValueError):
        extract_json("not json at all")


def test_panels_from_json_accepts_list_or_dict():
    assert panels_from_json([{"a": 1}]) == [{"a": 1}]
    assert panels_from_json({"panels": [{"a": 1}]}) == [{"a": 1}]


def test_pdf_text_is_latin1_safe():
    text = _pdf_text("It\u2019s a \u201cgreat\u201d day \u2014 caf\u00e9 \U0001F98A " + "x" * 300)
    assert "\u2019" not in text
    text.encode("latin-1")  # must not raise
    assert all(len(line) <= 90 for line in text.splitlines())
