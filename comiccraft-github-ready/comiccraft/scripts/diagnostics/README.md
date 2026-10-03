# Diagnostic scripts

Manual, one-off probe scripts used while choosing an image-generation backend
(Hugging Face Inference Providers, Spaces, Pollinations, local Stable Diffusion).

They call live external services and need valid API keys / a running server, so they are
**not** part of the automated test suite (`pytest` only runs `tests/`).

Run one directly from the project root, for example:

```bash
python scripts/diagnostics/test_tiny_sd.py
# test_comic_generation.py expects the app to be running: uvicorn app.main:app
python scripts/diagnostics/test_comic_generation.py
```
