from huggingface_hub import HfApi

api = HfApi()
spaces = list(api.list_spaces(search="flux-1-schnell", limit=30))
print(f"Total spaces found: {len(spaces)}")
for sp in spaces:
    try:
        r = api.get_space_runtime(sp.id)
        if r.stage == "RUNNING":
            print(f"RUNNING: {sp.id} (hardware: {r.hardware})")
    except Exception as e:
        pass
