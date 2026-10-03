import time
import requests
import urllib.parse
from PIL import Image
import io

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

for i in range(1, 6):
    prompt = f"Comic book panel {i} of Nova the hacker in a cyberpunk city with neon lights"
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}"
    
    t0 = time.time()
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200 and len(resp.content) > 1024:
            img = Image.open(io.BytesIO(resp.content))
            print(f"Panel {i} SUCCESS ({resp.status_code}) in {time.time()-t0:.1f}s, size={img.size}")
        else:
            print(f"Panel {i} FAILED ({resp.status_code}) in {time.time()-t0:.1f}s, body={resp.text[:100]}")
    except Exception as e:
        print(f"Panel {i} ERROR in {time.time()-t0:.1f}s: {e}")
    
    if i < 5:
        time.sleep(3)
