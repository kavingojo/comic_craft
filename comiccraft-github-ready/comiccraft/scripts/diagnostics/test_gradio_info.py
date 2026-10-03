import requests, json

for name, base in [
    ("flux-schnell", "https://black-forest-labs-flux-1-schnell.hf.space"),
    ("sd-3.5-turbo", "https://stabilityai-stable-diffusion-3-5-large-turbo.hf.space"),
    ("flux-dev", "https://black-forest-labs-flux-1-dev.hf.space")
]:
    try:
        r = requests.get(f"{base}/gradio_api/info", timeout=10)
        print(f"=== {name} ({r.status_code}) ===")
        if r.status_code == 200:
            info = r.json()
            named_endpoints = info.get("named_endpoints", {})
            for ep_name, ep_data in named_endpoints.items():
                print(f"  Endpoint: {ep_name}")
                parameters = ep_data.get("parameters", [])
                print(f"    Params ({len(parameters)}):", [p.get("label") or p.get("parameter_name") for p in parameters])
    except Exception as e:
        print(f"Error {name}: {e}")
