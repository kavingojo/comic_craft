import requests
from app.config import get_settings

s = get_settings()
headers = {"Authorization": f"Bearer {s.hf_token}"}
models = [
    "black-forest-labs/FLUX.1-schnell",
    "stabilityai/stable-diffusion-xl-base-1.0",
    "stabilityai/stable-diffusion-3.5-large",
    "runwayml/stable-diffusion-v1-5"
]

for m in models:
    url = f"https://api-inference.huggingface.co/models/{m}"
    try:
        r = requests.post(url, headers=headers, json={"inputs": "A cute cat"}, timeout=15)
        print(f"Model {m}: status={r.status_code}, len={len(r.content)}, text={r.text[:100]}")
    except Exception as e:
        print(f"Model {m}: error={e}")
