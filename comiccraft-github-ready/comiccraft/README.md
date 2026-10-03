# ComicCraft - AI Comic Story Creator (FastAPI + Gemini + Stable Diffusion/FLUX)

Enter a story idea, character, setting, tone and art style. ComicCraft writes a 5-panel outline
(Gemini Flash), expands it into narration and dialogue (Gemini Pro), draws every panel
(Hugging Face image model), shows a preview page and exports a PDF.

## What was fixed in this version (images not showing on the preview page)

* Panel images are now **embedded directly in the preview page** (base64), so they display even if
  the `/static` URL cannot be reached. The normal `/static/panels/...` URL is kept as a fallback.
* Images are saved as verified JPEG files; blank/black images (content-filter output) are rejected.
* Image generation tries **several models in order** (FLUX.1-schnell, SDXL, FLUX.1-dev, SD 3.5).
  The old default (`stable-diffusion-3.5-large`) is gated and often unavailable through providers.
* If every model fails, a labelled placeholder is shown **and the exact reason is printed in a yellow
  warning box** on the preview page (missing token, no access, etc.) - no more silent blank output.
* `.env` is loaded from the project folder regardless of where you start the server.
* Gemini model names are a fallback list, and replies are parsed tolerantly (no strict schema crashes).
* Download button uses a safe `/download/<file>` route and then opens the export-success page.

## Project structure

```text
comiccraft/
├── app/
│   ├── main.py            FastAPI app, static files, /health
│   ├── routes.py          /, /generate, /generate-comic/json, /download, /export-success, /test-image
│   ├── config.py          settings loaded from .env
│   ├── schemas.py         Pydantic models
│   ├── workflow.py        outline -> story -> images -> layout -> PDF
│   └── services/
│       ├── gemini_flash.py     5-panel outline
│       ├── gemini_pro.py       narration + dialogue
│       ├── image_generator.py  image generation, fallbacks, placeholders
│       ├── layout_builder.py   panel layout
│       ├── exporters.py        PDF export (FPDF2)
│       ├── llm_utils.py        Gemini client + JSON parsing
│       ├── media.py            /static URL -> file / data URI helpers
│       └── demo.py             offline demo content
├── templates/   index.html, comic_preview.html, export_success.html
├── static/      css/, panels/ (generated images), exports/ (generated PDFs)
├── tests/       automated pytest suite (runs offline in DEMO_MODE)
├── scripts/
│   └── diagnostics/   manual probe scripts for image backends (need network/keys)
├── docs/        SOURCE_MAPPING.md
├── .env.example copy to .env and add your own keys (never commit .env)
├── requirements.txt / requirements-dev.txt / requirements-local.txt
└── README.md
```

## Quick start (any OS)

```bash
git clone <your-repo-url> comiccraft && cd comiccraft
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # then add your GEMINI_API_KEY and HF_TOKEN
uvicorn app.main:app --reload                        # http://127.0.0.1:8000
```

No keys yet? Set `DEMO_MODE=true` in `.env` to try the whole flow with placeholder art.

> **Security:** `.env` is git-ignored. Never commit real API keys; if a key was ever shared or
> committed, revoke it and create a new one.

## Setup in VS Code (Windows)

1. Install **Python 3.10+** (tick "Add Python to PATH").
2. Unzip the project, then in VS Code: **File -> Open Folder -> comiccraft**.
3. Open a terminal: **Terminal -> New Terminal**, then:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

   macOS/Linux: `source .venv/bin/activate` instead of the activate line above.
   In VS Code press `Ctrl+Shift+P` -> "Python: Select Interpreter" -> choose `.venv`.

4. Create your settings file:

```powershell
copy .env.example .env
```

5. Open `.env` and set:
   * `GEMINI_API_KEY` - from https://aistudio.google.com/apikey
   * `HF_TOKEN` - from https://huggingface.co/settings/tokens (create a **fine-grained** token and tick
     **"Make calls to Inference Providers"**). `HF_API_KEY` works as a name too.

6. Run:

```powershell
uvicorn app.main:app --reload
```

7. Open http://127.0.0.1:8000 (API docs: http://127.0.0.1:8000/docs).

## Testing step by step

1. **Health check** - open http://127.0.0.1:8000/health. You should see `"gemini_key_set": true` and
   `"hf_token_set": true`.
2. **Smoke test without any keys** - set `DEMO_MODE=true` in `.env`, restart, create a comic. You get
   placeholder panels plus a PDF. This proves routing, templates, images and the PDF work.
   Set it back to `false` for real AI output.
3. **Image test** - open http://127.0.0.1:8000/test-image . On success it returns a `path`; open
   `http://127.0.0.1:8000<path>` to see the picture. On failure the error lists each model's reason.
4. **Full comic** - on the home page fill in the form and press *Generate Comic* (1-3 minutes).
5. **Automated tests** (optional):

```powershell
pip install -r requirements-dev.txt
python -m pytest
```

The automated suite lives in `tests/`. The scripts in `scripts/diagnostics/` are manual probes
against live services and are intentionally not collected by pytest.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Yellow warning: `HF_TOKEN is not set` | Put your token in `.env` and restart Uvicorn. |
| Warning lists `403` / `401` / `not supported` for a model | Token lacks the "Inference Providers" permission, or the model is gated. FLUX.1-schnell needs no approval; other models may need you to accept their licence on huggingface.co. |
| `402` / credits / rate limit | Your Hugging Face inference credits are used up; wait or upgrade, or use `IMAGE_BACKEND=local`. |
| Gemini error "model not found" | Edit `GEMINI_MODEL_OUTLINE` / `GEMINI_MODEL_STORY` in `.env` to a model your key can use (see https://ai.google.dev/gemini-api/docs/models). |
| Changed `.env` but nothing changed | Stop and restart Uvicorn (settings are read at start-up). |

## Run the image model on your own computer (optional)

```powershell
pip install -r requirements-local.txt
```

Set `IMAGE_BACKEND=local` in `.env`. The first run downloads a few GB; a GPU is strongly recommended.

## API example

`POST /generate-comic/json`

```json
{
  "story_prompt": "A brave fox exploring an enchanted forest",
  "character_name": "Finn",
  "setting": "Forest",
  "tone": "Dramatic",
  "art_style": "Comic book"
}
```

Returns `layout` (panel text + image paths), `pdf_path`, `pdf_filename` and `warnings`.
