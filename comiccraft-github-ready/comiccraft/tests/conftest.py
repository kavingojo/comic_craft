import os

# Must be set before any `app` module is imported so the tests never call real AI services.
os.environ["DEMO_MODE"] = "true"
os.environ.setdefault("GEMINI_API_KEY", "")
os.environ.setdefault("HF_TOKEN", "")
