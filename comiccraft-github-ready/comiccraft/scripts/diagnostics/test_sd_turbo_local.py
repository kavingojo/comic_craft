import time
import torch
from diffusers import AutoPipelineForText2Image

print("Testing sd-turbo on CPU...")
t0 = time.time()
try:
    pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sd-turbo", torch_dtype=torch.float32)
    pipe = pipe.to("cpu")
    print(f"Pipeline loaded in {time.time() - t0:.1f}s")
    
    t1 = time.time()
    image = pipe("Comic panel of a superhero flying over a city, comic book art", num_inference_steps=1, guidance_scale=0.0).images[0]
    print(f"Generated image in {time.time() - t1:.1f}s, size={image.size}")
    image.save("test_local_sd_turbo.jpg")
    print("Saved test_local_sd_turbo.jpg successfully!")
except Exception as e:
    print("sd-turbo failed:", e)
