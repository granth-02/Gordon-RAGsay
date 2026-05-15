from google import genai
from google.genai import types
import PIL.Image
from dotenv import load_dotenv
import os
import io

load_dotenv()
api = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api)

def call_llm(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=prompt
    )
    return response.text

def call_vision(image_path: str, prompt: str) -> str:
    # convert any image format to JPEG to avoid MPO/unsupported MIME errors
    img = PIL.Image.open(image_path)
    img = img.convert("RGB")  # strips MPO, RGBA, palette modes
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    jpeg_img = PIL.Image.open(buf)
    
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=[prompt, jpeg_img]
    )
    return response.text
