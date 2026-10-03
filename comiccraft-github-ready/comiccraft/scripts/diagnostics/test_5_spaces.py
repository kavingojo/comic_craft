import sys
from pathlib import Path

# Ensure comiccraft app is imported
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import time
from app.services.image_generator import _hf_space_image

for i in range(1, 6):
    t0 = time.time()
    try:
        print(f"Generating panel {i}...")
        img = _hf_space_image(f"Comic panel {i} of a detective in cyberpunk city")
        print(f"Panel {i} SUCCESS in {time.time() - t0:.1f}s, size={img.size}")
    except Exception as e:
        print(f"Panel {i} FAILED in {time.time() - t0:.1f}s: {e}")
