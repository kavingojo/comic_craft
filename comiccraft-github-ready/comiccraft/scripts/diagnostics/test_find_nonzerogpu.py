from huggingface_hub import HfApi
from app.config import get_settings

s = get_settings()
api = HfApi(token=s.hf_token)

spaces = list(api.list_spaces(search="diffusion", limit=50))
for sp in spaces:
    try:
        r = api.get_space_runtime(sp.id)
        if r.stage == "RUNNING" and r.hardware and "zero" not in r.hardware.lower():
            print(f"Non-Zero Space: {sp.id}, hardware={r.hardware}")
    except Exception:
        pass
