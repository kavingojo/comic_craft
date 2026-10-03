import requests, json

headers = {"User-Agent": "Mozilla/5.0"}
spaces_to_test = [
    "ChristianHappy/FLUX.1-schnell",
    "Niansuh/FLUX.1-schnell",
    "Rooc/FLUX.1-schnell",
    "affgg/black-forest-labs-FLUX.1-schnell",
    "Z1n3x/black-forest-labs-FLUX.1-schnell",
    "Daemon966/black-forest-labs-FLUX.1-schnell",
    "ersaz9396/black-forest-labs-FLUX.1-schnell",
    "ExportImage/black-forest-labs-FLUX.1-schnell",
    "roxtail/black-forest-labs-FLUX.1-schnell",
    "jorgenaveiras/black-forest-labs-FLUX.1-schnell",
]

for sp in spaces_to_test:
    subdomain = sp.replace("/", "-").lower()
    url = f"https://{subdomain}.hf.space"
    try:
        r = requests.get(f"{url}/gradio_api/info", timeout=5)
        print(f"Space {sp} info status: {r.status_code}")
    except Exception as e:
        print(f"Space {sp} failed: {type(e).__name__}")
