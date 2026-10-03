import time
import torch
from diffusers import StableDiffusionPipeline

torch.set_num_threads(6)
t0 = time.time()
pipe = StableDiffusionPipeline.from_pretrained("segmind/tiny-sd", torch_dtype=torch.float32)
pipe = pipe.to("cpu")
print(f"Loaded in {time.time() - t0:.2f}s")

t1 = time.time()
img = pipe("Comic panel of Nova the hacker in cyber room", num_inference_steps=5, guidance_scale=6.0).images[0]
print(f"Generated 5 steps in {time.time() - t1:.2f}s!")
img.save("test_nova_5steps.jpg")
