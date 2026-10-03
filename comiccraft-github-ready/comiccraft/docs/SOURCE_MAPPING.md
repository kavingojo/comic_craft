# Source-document mapping

| Document item | File |
|---|---|
| Gemini Flash outline (`generate_outline`) | `app/services/gemini_flash.py` |
| Gemini Pro narration/dialogue (`generate_story`) | `app/services/gemini_pro.py` |
| Stable Diffusion images (`generate_image`) | `app/services/image_generator.py` |
| Layout binding (`build_comic_layout`) | `app/services/layout_builder.py` |
| PDF generation with FPDF (`save_pdf`) | `app/services/exporters.py` |
| Routes `/`, `/generate`, `/generate-comic/json`, `/export-success`, `/test-image` | `app/routes.py` |
| Jinja2 pages | `templates/index.html`, `comic_preview.html`, `export_success.html` |
| Environment variables | `app/config.py`, `.env.example` |

Deliberate updates to the document's stack (the referenced items are retired or unreliable today):
`google-generativeai` -> `google-genai`; Gemini 1.5 (shut down) -> configurable current Gemini models with
fallbacks; `runwayml/stable-diffusion-v1-5` (repository removed) -> hosted FLUX/SDXL with fallbacks, and
`stable-diffusion-v1-5/stable-diffusion-v1-5` for the optional local backend.
