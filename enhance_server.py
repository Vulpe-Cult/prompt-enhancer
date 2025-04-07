import os
import re  # Важно: этот импорт должен быть в начале файла
from flask import Flask, request, jsonify
from llama_cpp import Llama
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

app = Flask(__name__)

# Конфигурация модели
MODEL_PATH = "/app/models/mistral-7b-instruct-v0.1.Q4_0.gguf"
MODEL_URL = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_0.gguf"
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("Hugging Face token not found. Please set HF_TOKEN in .env file")

DEFAULT_NEGATIVE_PROMPT = (
    "low quality, blurry, distorted anatomy, extra limbs, deformed hands, bad proportions, "
    "ugly, duplicate, morbid, mutilated, bad anatomy, disfigured, poorly drawn face, "
    "mutation, deformed, extra fingers, poorly drawn hands, missing limbs, text, watermark, "
    "signature, out of focus, long neck, extra arms, extra legs, fused fingers"
)

def download_model():
    """Скачивает модель, если она отсутствует"""
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        with requests.get(MODEL_URL, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(MODEL_PATH, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("Model downloaded successfully")
    except Exception as e:
        print(f"Failed to download model: {e}")
        raise

# Проверяем и скачиваем модель при запуске
if not os.path.exists(MODEL_PATH):
    print("Model not found, downloading...")
    download_model()

# Инициализируем модель с более оптимальными параметрами
try:
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_threads=4,
        verbose=False  # Отключаем лишние логи llama.cpp
    )
    print("Model loaded successfully")
except Exception as e:
    print(f"Failed to load model: {e}")
    raise

def generate_positive_prompt(russian_prompt):
    """Генерирует позитивный промпт на основе русского описания"""
    # Упрощенный и более четкий промпт для модели
    instruction = f"""Переведи на английский и улучши этот промпт для Stable Diffusion. 
    Сделай его детализированным и конкретным. Ответ должен быть только на английском, 
    в формате: "детальное описание, художественный стиль, качество".
    
    Исходный промпт: "{russian_prompt}"
    
    Пример хорошего ответа:
    "a modern living room with large windows, leather sofa and abstract paintings on the walls, 
    minimalist design with warm lighting, ultra detailed, 4k, photorealistic"
    """
    
    try:
        # Убираем дублирующийся <s> из промпта (видно из логов предупреждение)
        response = llm(
            f"[INST] {instruction} [/INST]",
            max_tokens=400,
            temperature=0.7,
            top_p=0.9,
            stop=["</s>"],
            echo=False
        )
        
        prompt = response['choices'][0]['text'].strip()
        
        # Упрощенная очистка промпта
        prompt = prompt.replace('"', '').replace("'", "").strip()
        if not prompt:
            return "high quality digital artwork"
            
        return prompt
    except Exception as e:
        print(f"Prompt generation error: {str(e)}")
        return "high quality digital artwork"

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "model": "loaded" if os.path.exists(MODEL_PATH) else "missing"
    })

@app.route("/enhance", methods=["POST"])
def enhance_prompt():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    input_text = data.get("text", "").strip()
    
    if not input_text:
        return jsonify({"error": "Text is required"}), 400
    
    try:
        positive_prompt = generate_positive_prompt(input_text)
        
        return jsonify({
            "positive": positive_prompt,
            "negative": DEFAULT_NEGATIVE_PROMPT,
            "input_text": input_text
        })
    except Exception as e:
        return jsonify({
            "positive": "high quality digital artwork",
            "negative": DEFAULT_NEGATIVE_PROMPT,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
