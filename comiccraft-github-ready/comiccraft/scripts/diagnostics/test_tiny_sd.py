import time
import torch
from diffusers import StableDiffusionPipeline

print("Testing segmind/tiny-sd on CPU...")
t0 = time.time()
try:
    pipe = StableDiffusionPipeline.from_pretrained("segmind/tiny-sd", torch_dtype=torch.float32)
    pipe = pipe.to("cpu")
    print(f"Tiny-SD loaded in {time.time() - t0:.1f}s")
    
    t1 = time.time()
    image = pipe("Comic panel of a superhero flying over a city, comic book art", num_inference_steps=8, guidance_scale=7.5).images[0]
    print(f"Generated image in {time.time() - t1:.1f}s, size={image.size}")
    image.save("test_tiny_sd.jpg")
    print("Saved test_tiny_sd.jpg successfully!")
except Exception as e:
    print("tiny-sd failed:", e)
