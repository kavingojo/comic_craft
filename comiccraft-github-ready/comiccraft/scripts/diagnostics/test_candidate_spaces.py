from gradio_client import Client

candidate_spaces = [
    "mrfakename/FLUX.1-schnell-turbo",
    "ByteDance/SDXL-Lightning",
    "radames/Real-Time-SD-Turbo",
    "ginipick/text-to-image",
    "multimodalart/flux-tarot-v1",
    "ehristoforu/dalle-3-xl-lora-v2",
    "KingNish/Realtime-FLUX",
]

for space_name in candidate_spaces:
    try:
        print(f"Trying {space_name}...")
        c = Client(space_name)
        print(f"  Connected to {space_name}! Endpoints: {list(c.endpoints.keys())}")
    except Exception as e:
        print(f"  Failed {space_name}: {type(e).__name__} {str(e)[:80]}")
