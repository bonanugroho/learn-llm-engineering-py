import os

from dotenv import load_dotenv

import gradio as gr
from io import BytesIO
from PIL import Image

from huggingface_hub import login
import torch
from diffusers import StableDiffusionPipeline

load_dotenv(override=True)
hf_token = os.getenv('HF_TOKEN')

if hf_token:
    print(f"Hugging Face Token exists and begins {hf_token[:5]}")
else:
    print("Hugging Face Token not set")

login(hf_token, add_to_git_credential=True)

def create_image(prompt):
    model_id = "OFA-Sys/small-stable-diffusion-v0"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to("cuda")
    pipe.enable_model_cpu_offload()


    # prompt = "A futuristic class full of students learning AI coding in the surreal style of Salvador Dali"
    image = pipe(prompt).images[0]
    # return Image.open(BytesIO(image))
    return image

print("Torch with cuda available : ",torch.cuda.is_available())

gr.Interface(fn=create_image, inputs="textbox", outputs=[gr.Image()], flagging_mode="never").launch(share=False)

# with gr.blocks as ui:
#     with gr.Row():
#         image_output = gr.Image(height=500)
#     with gr.Row():
#         entry = gr.Textbox(label="Chat with our AI Assistant:")
#     with gr.Row():
#         clear = gr.Button("Clear")

