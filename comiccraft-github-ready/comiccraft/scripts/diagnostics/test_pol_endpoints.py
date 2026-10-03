import requests

urls = [
    "https://image.pollinations.ai/prompt/a%20happy%20dog",
    "https://image.pollinations.ai/prompt/a%20happy%20cat?nologo=true",
    "https://image.pollinations.ai/prompt/a%20happy%20bird?model=turbo",
    "https://image.pollinations.ai/prompt/a%20happy%20fish?model=flux",
    "https://gen.pollinations.ai/image/a%20happy%20lion",
]

for u in urls:
    try:
        r = requests.get(u, headers={"User-Agent": "ComicCraft/1.0"}, timeout=15)
        print(f"URL: {u[:45]}... => Status: {r.status_code}, Length: {len(r.content)}")
    except Exception as e:
        print(f"URL: {u[:45]}... => Error: {e}")
