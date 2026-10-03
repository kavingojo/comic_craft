from huggingface_hub import HfApi
from app.config import get_settings

s = get_settings()
api = HfApi(token=s.hf_token)

models_search = ["sd-turbo", "sdxl-turbo", "flux", "stable-diffusion", "comic", "anime"]
found = []
for m in models_search:
    spaces = list(api.list_spaces(search=m, limit=40))
    for sp in spaces:
        if getattr(sp, "likes", 0) > 5:
            try:
                r = api.get_space_runtime(sp.id)
                if r.stage == "RUNNING":
                    found.append((sp.id, r.hardware, getattr(sp, "likes", 0)))
            except Exception:
                pass

for item in sorted(found, key=lambda x: -x[2]):
    print(f"Space: {item[0]} | hardware: {item[1]} | likes: {item[2]}")
