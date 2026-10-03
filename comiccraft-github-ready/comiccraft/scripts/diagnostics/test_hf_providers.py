from huggingface_hub import InferenceClient
from app.config import get_settings

s = get_settings()
providers = ["fal-ai", "replicate", "together", "sambanova", "novita", "hyperbolic", "nebius"]

for p in providers:
    try:
        c = InferenceClient(provider=p, api_key=s.hf_token)
        print(f"Testing provider {p}...")
        img = c.text_to_image("a cute cat in comic style", model="black-forest-labs/FLUX.1-schnell")
        print(f"  SUCCESS {p}: {type(img)}")
    except Exception as e:
        err = str(e)
        print(f"  FAILED {p}: {err[:120]}")
