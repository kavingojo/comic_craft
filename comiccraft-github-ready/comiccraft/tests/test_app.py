"""End-to-end test in DEMO_MODE (no API keys needed): form -> preview with images -> PDF download."""
import re

import pytest

pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)
FORM = {
    "story_prompt": "A brave fox exploring an enchanted forest",
    "character_name": "Finn",
    "setting": "Forest",
    "tone": "Dramatic",
    "art_style": "Anime",
}


def test_home_and_health():
    assert client.get("/").status_code == 200
    body = client.get("/health").json()
    assert body["status"] == "ok" and body["demo_mode"] is True


def test_generate_shows_five_inline_images_and_pdf_downloads():
    response = client.post("/generate", data=FORM)
    assert response.status_code == 200
    html = response.text
    assert len(re.findall(r'src="data:image/jpeg;base64,', html)) == 5

    # The regular /static URL must work too.
    static_url = re.search(r'data-fallback="(/static/panels/[^"]+)"', html).group(1)
    image = client.get(static_url)
    assert image.status_code == 200 and image.headers["content-type"].startswith("image/")

    pdf_name = re.search(r'href="/download/(comiccraft_[0-9_]+\.pdf)"', html).group(1)
    pdf = client.get(f"/download/{pdf_name}")
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")
    assert client.get(f"/export-success?filename={pdf_name}").status_code == 200


def test_json_api():
    response = client.post("/generate-comic/json", json=FORM)
    assert response.status_code == 200
    data = response.json()
    assert len(data["layout"]) == 5 and data["pdf_path"].endswith(".pdf")


def test_download_rejects_bad_names():
    assert client.get("/download/..%2Fsecret.txt").status_code in (400, 404)
    assert client.get("/download/evil.pdf").status_code == 400
