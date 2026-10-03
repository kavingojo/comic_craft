from huggingface_hub import HfApi
from app.config import get_settings

s = get_settings()
api = HfApi(token=s.hf_token)
for term in ["sdxl", "sd-turbo", "stable-diffusion"]:
    print(f"=== Search: {term} ===")
    spaces = list(api.list_spaces(search=term, limit=5))
    for sp in spaces:
        print("  Space:", sp.id, "likes:", getattr(sp, "likes", 0))
