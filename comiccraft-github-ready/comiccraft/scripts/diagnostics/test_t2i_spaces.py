from huggingface_hub import HfApi
from app.config import get_settings

s = get_settings()
api = HfApi(token=s.hf_token)
spaces = list(api.list_spaces(search="text-to-image", limit=20))
for sp in spaces:
    try:
        runtime = api.get_space_runtime(sp.id)
        if runtime.stage == "RUNNING":
            print(f"{sp.id} | hardware={runtime.hardware} | likes={getattr(sp, 'likes', 0)}")
    except Exception:
        pass
