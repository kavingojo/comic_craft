import time
from app.services.image_generator import _hf_space_image

for i in range(1, 6):
    t0 = time.time()
    try:
        img = _hf_space_image(f"Comic panel {i} of a detective walking in a rainy neon cyberpunk city")
        print(f"Panel {i} success in {time.time() - t0:.1f}s, size={img.size}")
    except Exception as e:
        print(f"Panel {i} FAILED in {time.time() - t0:.1f}s: {e}")
