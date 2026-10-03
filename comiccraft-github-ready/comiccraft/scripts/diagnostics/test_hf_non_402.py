from huggingface_hub import HfApi, InferenceClient
from app.config import get_settings

s = get_settings()
api = HfApi(token=s.hf_token)
client = InferenceClient(api_key=s.hf_token)

models = list(api.list_models(filter="text-to-image", sort="likes", limit=40))
print(f"Testing {len(models)} models for free inference...")

for m in models:
    # Try calling text_to_image
    try:
        res = client.text_to_image("a small cat", model=m.id)
        print(f"SUCCESS: {m.id} -> {type(res)}")
        break
    except Exception as e:
        err = str(e)
        if "402" not in err and "depleted" not in err:
            print(f"Non-402 Error on {m.id}: {err[:80]}")
