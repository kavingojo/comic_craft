from huggingface_hub import HfApi
from app.config import get_settings

s = get_settings()
api = HfApi(token=s.hf_token)

models = list(api.list_models(filter="text-to-image", sort="downloads", limit=25))
for m in models:
    info = api.model_info(m.id)
    inference = getattr(info, "inference", None)
    disabled = getattr(info, "disabled", None)
    print(f"{m.id}: inference={inference}, disabled={disabled}")
