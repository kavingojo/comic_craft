from huggingface_hub import HfApi
from app.config import get_settings

s = get_settings()
api = HfApi(token=s.hf_token)

for q in ["flux", "sdxl", "diffusion", "stable diffusion"]:
    spaces = list(api.list_spaces(search=q, limit=10))
    for sp in spaces:
        try:
            runtime = api.get_space_runtime(sp.id)
            print(f"{sp.id} | hardware={runtime.hardware} | stage={runtime.stage}")
        except Exception:
            pass
