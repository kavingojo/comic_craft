from huggingface_hub import HfApi
import requests

s = HfApi()
spaces = list(s.list_spaces(search="text-to-image", limit=20))
for sp in spaces:
    sub = sp.id.replace("/", "-").replace(".", "-").lower()
    url = f"https://{sub}.hf.space/gradio_api/info"
    try:
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            endpoints = list(r.json().get("named_endpoints", {}).keys())
            if any(e in endpoints for e in ["/infer", "/predict", "/generate", "/text2img"]):
                print(f"MATCH: {sp.id} -> {endpoints}")
    except Exception:
        pass
