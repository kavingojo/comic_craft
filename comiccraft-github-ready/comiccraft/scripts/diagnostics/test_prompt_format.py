import requests
import urllib.parse

prompts = [
    "Nova the hacker",
    "Nova_the_hacker",
    "Comic book panel 1 of Nova the hacker in a cyberpunk city",
    "Comic_book_panel_1_of_Nova_the_hacker_in_a_cyberpunk_city",
]

for p in prompts:
    enc = urllib.parse.quote(p)
    url = f"https://image.pollinations.ai/prompt/{enc}"
    try:
        r = requests.get(url, timeout=15)
        print(f"Prompt: {p[:30]}... -> status={r.status_code}, len={len(r.content)}")
    except Exception as e:
        print(f"Prompt: {p[:30]}... -> error={e}")
