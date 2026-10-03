import time
import requests
import io
import urllib.parse
from PIL import Image

def generate_pollinations_default(prompt: str, width: int = 768, height: int = 768) -> Image.Image:
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&seed={int(time.time()*1000)%100000}"
    headers = {"User-Agent": "ComicCraft/1.0"}
    resp = requests.get(url, headers=headers, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"Pollinations HTTP {resp.status_code}: {resp.text[:100]}")
    img = Image.open(io.BytesIO(resp.content))
    return img.convert("RGB")

for i in range(1, 6):
    t0 = time.time()
    try:
        print(f"Generating panel {i} via Pollinations (default)...")
        img = generate_pollinations_default(f"Comic panel {i} of Nova the hacker typing at keyboard, glowing futuristic room, comic book art")
        print(f"Panel {i} SUCCESS in {time.time() - t0:.1f}s, size={img.size}, format={img.format}")
    except Exception as e:
        print(f"Panel {i} FAILED in {time.time() - t0:.1f}s: {e}")
