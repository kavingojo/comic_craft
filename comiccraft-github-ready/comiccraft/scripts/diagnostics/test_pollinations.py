import requests
from PIL import Image
import io

print("Testing Pollinations.ai...")
url = "https://image.pollinations.ai/prompt/comic%20panel%20of%20a%20detective%20in%20cyberpunk%20city?width=768&height=768&nologo=true"
headers = {"User-Agent": "ComicCraft/1.0"}
try:
    resp = requests.get(url, headers=headers, timeout=30)
    print("Pollinations status:", resp.status_code, "Length:", len(resp.content), "Content-Type:", resp.headers.get("content-type"))
    img = Image.open(io.BytesIO(resp.content))
    print("Pollinations Image successfully loaded:", img.size, img.format)
except Exception as e:
    print("Pollinations failed:", e)
