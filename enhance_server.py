import os
import re
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения из .env
load_dotenv()

app = Flask(__name__)

# Конфигурация из переменных окружения
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/mistral-7b-instruct-v0.1.Q4_0.gguf")
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found. Please set it in .env file")

LLAMA_N_CTX = int(os.getenv("LLAMA_N_CTX", "2048"))
LLAMA_N_THREADS = int(os.getenv("LLAMA_N_THREADS", "4"))
LLAMA_VERBOSE = os.getenv("LLAMA_VERBOSE", "false").lower() == "true"

# Глобальная переменная для ленивой инициализации модели
_llm = None

DEFAULT_NEGATIVE_PROMPT = (
    "low quality, blurry, distorted anatomy, extra limbs, deformed hands, bad proportions, "
    "ugly, duplicate, morbid, mutilated, bad anatomy, disfigured, poorly drawn face, "
    "mutation, deformed, extra fingers, poorly drawn hands, missing limbs, text, watermark, "
    "signature, out of focus, long neck, extra arms, extra legs, fused fingers"
)

def get_llm():
    """Ленивая загрузка модели (только при первом вызове)"""
    global _llm
    if _llm is None:
        from llama_cpp import Llama
        logger.info(f"Loading model from {MODEL_PATH}")
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Run download_model.py first or check volume mount."
            )
        _llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=LLAMA_N_CTX,
            n_threads=LLAMA_N_THREADS,
            verbose=LLAMA_VERBOSE
        )
        logger.info("Model loaded successfully")
    return _llm

def generate_positive_prompt(russian_prompt):
    """Генерирует позитивный промпт на основе русского описания"""
    instruction = f"""Convert the following Russian prompt into an English prompt for Stable Diffusion.
Make it detailed, specific, and include style and quality keywords.
Respond ONLY with the English prompt, no extra text.

Original prompt: "{russian_prompt}"

Example of a good response:
"a futuristic city with flying cars, neon lights, cyberpunk style, highly detailed, 8k, cinematic lighting"
""
    try:
        llm_instance = get_llm()
        response = llm_instance(
            f"[INST] {instruction} [/INST]",
            max_tokens=400,
            temperature=0.7,
            top_p=0.9,
            stop=["</s>"],
            echo=False
        )
        prompt = response['choices'][0]['text'].strip()
        prompt = re.sub(r'["\']', '', prompt).strip()
        if not prompt:
            logger.warning("Empty prompt generated, using fallback")
            return "high quality digital artwork"
        logger.info(f"Generated prompt for input: {russian_prompt[:50]}...")
        return prompt
    except Exception as e:
        logger.error(f"Prompt generation error: {str(e)}")
        return "high quality digital artwork"

@app.route("/health", methods=["GET"])
def health_check():
    try:
        get_llm()  # проверяем, что модель загружается (или уже загружена)
        model_status = "loaded"
    except Exception as e:
        model_status = f"error: {str(e)}"
    return jsonify({
        "status": "ok",
        "model_status": model_status
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
        logger.exception("Unexpected error in /enhance")
        return jsonify({
            "positive": "high quality digital artwork",
            "negative": DEFAULT_NEGATIVE_PROMPT,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=8001, debug=debug_mode)
