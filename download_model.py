import os
import requests
from dotenv import load_dotenv

load_dotenv()

MODEL_PATH = "/app/models/mistral-7b-instruct-v0.1.Q4_0.gguf"
MODEL_URL = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_0.gguf"
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not set in environment")

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

headers = {"Authorization": f"Bearer {HF_TOKEN}"}
print(f"Downloading model from {MODEL_URL}")
response = requests.get(MODEL_URL, headers=headers, stream=True)
response.raise_for_status()

with open(MODEL_PATH, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)
print("Model downloaded successfully")
