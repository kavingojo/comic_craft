from app.schemas import ComicOutline, ComicStory, PanelOutline, PanelStory


def demo_outline(character: str, setting: str, tone: str, style: str) -> ComicOutline:
    panels = []
    beats = [
        ("A Strange Beginning", f"{character} discovers something unusual in {setting}."),
        ("The Discovery", f"The mystery grows as {character} explores {setting}."),
        ("A Difficult Choice", f"{character} faces a challenge that tests courage."),
        ("The Turning Point", "A clever decision changes the situation."),
        ("A New Day", f"The adventure ends with {character} learning something meaningful."),
    ]
    for i, (title, scene) in enumerate(beats, 1):
        panels.append(PanelOutline(panel_number=i, title=title, scene_description=scene,
            image_prompt=f"{style} comic art of {character} in {setting}, {scene}, {tone} mood"))
    return ComicOutline(panels=panels)


def demo_story(outline: ComicOutline, character: str) -> ComicStory:
    panels = []
    for p in outline.panels:
        panels.append(PanelStory(
            panel_number=p.panel_number, title=p.title, scene_description=p.scene_description,
            caption="The moment feels full of possibility.",
            narration=f"{character} takes a careful step forward, determined to discover what comes next.",
            dialogue=f'"Let’s see where this leads," {character} says.', image_prompt=p.image_prompt))
    return ComicStory(panels=panels)
