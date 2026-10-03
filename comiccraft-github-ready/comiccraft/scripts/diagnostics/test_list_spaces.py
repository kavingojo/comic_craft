from huggingface_hub import HfApi
from app.config import get_settings

s = get_settings()
api = HfApi(token=s.hf_token)
spaces = list(api.list_spaces(search="flux-1-schnell", limit=15))
for sp in spaces:
    print("Space:", sp.id, "likes:", getattr(sp, "likes", 0))
