from huggingface_hub import InferenceClient
from app.config import get_settings

s = get_settings()
client = InferenceClient(api_key=s.hf_token)

warm_models = [
    "Tongyi-MAI/Z-Image-Turbo",
    "playgroundai/playground-v2.5-1024px-aesthetic",
    "black-forest-labs/FLUX.2-klein-4B",
    "Qwen/Qwen-Image",
    "lightx2v/Qwen-Image-Lightning",
]

for m in warm_models:
    try:
        print(f"Testing {m}...")
        img = client.text_to_image("a superhero in comic book style", model=m)
        print(f"  SUCCESS {m}: {type(img)}")
    except Exception as e:
        print(f"  FAILED {m}: {type(e).__name__} {e}")
