import requests, json
from app.config import get_settings

s = get_settings()
headers = {
    "Authorization": f"Bearer {s.hf_token}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
base = "https://stabilityai-stable-diffusion-3-5-large-turbo.hf.space"
call_res = requests.post(
    f"{base}/gradio_api/call/infer",
    json={"data": ["A cyberpunk comic book panel of a detective", "", 0, True, 768, 768, 1.0, 4]},
    headers=headers,
    timeout=20,
)
print("call_res:", call_res.status_code, call_res.text)
event_id = call_res.json().get("event_id")
stream_res = requests.get(f"{base}/gradio_api/call/infer/{event_id}", headers=headers, stream=True, timeout=60)
for line in stream_res.iter_lines():
    if line:
        decoded = line.decode("utf-8", errors="ignore")
        print("STREAM:", repr(decoded[:150]))
