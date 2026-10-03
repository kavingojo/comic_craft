import requests
from PIL import Image
import io

models = ["turbo", "dreamshaper", "flux", "flux-realism", "flux-anime", "flux-3d"]
for m in models:
    try:
        url = f"https://image.pollinations.ai/prompt/comic%20panel?width=512&height=512&model={m}&nologo=true"
        r = requests.get(url, headers={"User-Agent": "ComicCraft/1.0"}, timeout=15)
        print(f"Model {m}: status={r.status_code}, len={len(r.content)}")
    except Exception as e:
        print(f"Model {m}: error={e}")
