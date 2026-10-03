from google import genai
from app.config import get_settings

s = get_settings()
client = genai.Client(api_key=s.gemini_api_key)

models = [
    "gemini-3.1-flash-lite-image",
    "gemini-3.1-flash-image",
    "gemini-3.1-flash-image-preview",
    "gemini-3-pro-image",
    "gemini-3-pro-image-preview",
    "gemini-2.5-flash-image",
]

for m in models:
    try:
        print(f"Testing {m}...")
        resp = client.models.generate_content(
            model=m,
            contents="Generate a comic panel drawing of a cat",
        )
        print(f"  SUCCESS {m}: {resp}")
    except Exception as e:
        print(f"  FAILED {m}: {type(e).__name__} {e}")
