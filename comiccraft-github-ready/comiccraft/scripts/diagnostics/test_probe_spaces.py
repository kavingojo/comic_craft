from huggingface_hub import HfApi
import requests
import json
from app.config import get_settings

s = get_settings()
api = HfApi(token=s.hf_token)

spaces = list(api.list_spaces(search="text-to-image", limit=30))
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

print(f"Checking {len(spaces)} spaces...")
for sp in spaces:
    name = sp.id
    sub = name.replace("/", "-").replace(".", "-").lower()
    base = f"https://{sub}.hf.space"
    try:
        r = requests.get(f"{base}/gradio_api/info", headers=headers, timeout=5)
        if r.status_code == 200:
            info = r.json()
            endpoints = list(info.get("named_endpoints", {}).keys())
            print(f"[ONLINE] {name} -> {endpoints}")
    except Exception:
        pass
