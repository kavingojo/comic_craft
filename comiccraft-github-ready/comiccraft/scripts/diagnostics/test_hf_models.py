from huggingface_hub import InferenceClient
from app.config import get_settings

s = get_settings()
client = InferenceClient(api_key=s.hf_token)
test_models = [
    "black-forest-labs/FLUX.1-schnell",
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5",
    "CompVis/stable-diffusion-v1-4",
    "prompthero/openjourney"
]
for m in test_models:
    try:
        res = client.text_to_image("a cat", model=m)
        print(f"{m}: SUCCESS ({type(res)})")
    except Exception as e:
        print(f"{m}: FAILED ({e})")
