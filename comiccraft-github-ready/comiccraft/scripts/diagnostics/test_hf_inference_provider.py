from huggingface_hub import InferenceClient
from app.config import get_settings

s = get_settings()
models = [
    "black-forest-labs/FLUX.1-schnell",
    "stabilityai/stable-diffusion-xl-base-1.0",
    "stabilityai/stable-diffusion-3.5-large",
    "runwayml/stable-diffusion-v1-5",
    "stabilityai/sd-turbo",
    "stabilityai/sdxl-turbo",
]

client = InferenceClient(provider="hf-inference", api_key=s.hf_token)
for m in models:
    try:
        print(f"Testing {m} with provider='hf-inference'...")
        res = client.text_to_image("a comic cat", model=m)
        print(f"  SUCCESS {m}: {type(res)}")
    except Exception as e:
        print(f"  FAILED {m}: {type(e).__name__} - {e}")
