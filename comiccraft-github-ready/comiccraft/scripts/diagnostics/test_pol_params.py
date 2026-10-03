import requests

params_to_test = [
    ("clean", "https://image.pollinations.ai/prompt/a%20brave%20knight"),
    ("width_height_512", "https://image.pollinations.ai/prompt/a%20brave%20knight?width=512&height=512"),
    ("width_height_768", "https://image.pollinations.ai/prompt/a%20brave%20knight?width=768&height=768"),
    ("nologo", "https://image.pollinations.ai/prompt/a%20brave%20knight?nologo=true"),
    ("seed", "https://image.pollinations.ai/prompt/a%20brave%20knight?seed=42"),
    ("all", "https://image.pollinations.ai/prompt/a%20brave%20knight?width=768&height=768&nologo=true&seed=42"),
]

for label, url in params_to_test:
    try:
        r = requests.get(url, timeout=20)
        print(f"{label}: status={r.status_code}, len={len(r.content)}")
    except Exception as e:
        print(f"{label}: error={e}")
