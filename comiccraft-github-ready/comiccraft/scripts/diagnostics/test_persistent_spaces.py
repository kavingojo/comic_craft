from huggingface_hub import HfApi

api = HfApi()
# Search for spaces that might have persistent GPU
keywords = ["stable-diffusion", "sdxl", "flux", "generator", "diffusers"]
found = []
for kw in keywords:
    spaces = list(api.list_spaces(search=kw, limit=20))
    for sp in spaces:
        try:
            r = api.get_space_runtime(sp.id)
            if r.stage == "RUNNING" and r.hardware and "zero" not in r.hardware.lower():
                print(f"FOUND: {sp.id} | hardware={r.hardware}")
                found.append(sp.id)
        except Exception:
            pass

print(f"Total found: {len(found)}")
