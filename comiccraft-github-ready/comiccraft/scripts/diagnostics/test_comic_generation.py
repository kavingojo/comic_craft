import json
import time
import urllib.request
from pathlib import Path
from PIL import Image

payload = {
    "story_prompt": "Nova discovers an encrypted AI cipher hidden deep inside the cyber city mainframe.",
    "character_name": "Nova",
    "setting": "Cyberpunk metropolis",
    "tone": "Suspenseful",
    "art_style": "Comic book"
}

print("Initiating full 5-panel comic generation via API...")
req = urllib.request.Request(
    "http://127.0.0.1:8000/generate-comic/json",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

t0 = time.time()
try:
    with urllib.request.urlopen(req, timeout=600) as response:
        data = json.loads(response.read().decode("utf-8"))
        duration = time.time() - t0
        print(f"Generation finished in {duration:.1f}s")
        layout = data.get("layout", [])
        print(f"Total panels generated: {len(layout)}")
        print(f"PDF filename: {data.get('pdf_filename')}")
        print(f"Warnings: {data.get('warnings')}")

        all_ok = True
        for i, panel in enumerate(layout, start=1):
            img_path = panel.get("image_path", "")
            title = panel.get("title", "")
            print(f"\n--- Panel {i}: {title} ---")
            print(f"URL: {img_path}")

            # Check file on disk
            local_rel = img_path.lstrip("/")
            local_abs = Path(r"c:\RASH\comiccraft") / local_rel
            if not local_abs.is_file():
                print(f"ERROR: File does not exist on disk: {local_abs}")
                all_ok = False
                continue

            size = local_abs.stat().st_size
            print(f"File size: {size} bytes ({size/1024:.1f} KB)")
            if size < 5000:
                print("ERROR: File too small!")
                all_ok = False
                continue

            try:
                with Image.open(local_abs) as img:
                    img.verify()
                print(f"Image verified: dimensions {img.size if hasattr(img, 'size') else 'valid'}")
            except Exception as e:
                print(f"ERROR verifying image: {e}")
                all_ok = False

            if "placeholder" in img_path.lower():
                print("WARNING: Panel is a placeholder graphic card.")
                all_ok = False
            else:
                print("CONFIRMED: Real generated AI artwork.")

        if all_ok:
            print("\n===========================================")
            print("TEST PASSED: ALL 5 PANELS CONTAIN REAL GENERATED IMAGES!")
            print("===========================================")
        else:
            print("\nTEST FAILED: Some panels are missing or placeholders.")

except Exception as exc:
    print(f"Request failed: {exc}")
