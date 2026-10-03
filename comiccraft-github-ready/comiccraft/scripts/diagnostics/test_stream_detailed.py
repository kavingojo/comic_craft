import requests, json

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
url = "https://black-forest-labs-flux-1-schnell.hf.space"
ep = "/gradio_api/call/infer"
data = ["comic panel of a detective", 0, True, 768, 768, 4]

call_res = requests.post(f"{url}{ep}", json={"data": data}, headers=headers, timeout=20)
print("call_res:", call_res.status_code, call_res.text)
event_id = call_res.json().get("event_id")

stream_res = requests.get(f"{url}{ep}/{event_id}", headers=headers, stream=True, timeout=60)
for line in stream_res.iter_lines():
    if line:
        decoded = line.decode("utf-8", errors="ignore")
        print("STREAM:", repr(decoded))
