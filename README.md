# Prompt Enhancer for Stable Diffusion

Микросервис для преобразования русских описаний в английские промпты для Stable Diffusion.  
Использует локальную LLM (Mistral-7B-Instruct в формате GGUF) и не требует внешних API.

##  Особенности

- Полностью локальная работа (никаких API‑ключей, кроме Hugging Face для скачивания модели)
- Ленивая загрузка модели (модель подгружается только при первом запросе)
- Docker‑ready с монтированием томов (модель скачивается один раз)
- Настраиваемые параметры модели через переменные окружения
- Эндпоинты: `/health` (проверка статуса) и `/enhance` (улучшение промпта)

##  Требования

- **Docker** 20.10+ и **Docker Compose** 1.29+
- **4 ГБ RAM** (рекомендуется 8 ГБ)
- **10 ГБ** свободного дискового пространства
- **Токен Hugging Face** (бесплатный, для скачивания модели)

##  Установка и запуск

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/Vulpe-Cult/prompt-enhancer.git
cd prompt-enhancer
```

### 2. Создайте файл .env с токеном Hugging Face

```bash
echo "HF_TOKEN=your_huggingface_token_here" > .env
```

### 3. Запустите сервис

```bash
docker compose up --build
```

При первом запуске модель автоматически скачается в папку models/ (около 4 ГБ).
Последующие запуски будут использовать уже скачанную модель.


Использование API
  Улучшение промпта
```bash
curl -X POST http://localhost:8001/enhance \
  -H "Content-Type: application/json" \
  -d '{"text":"красивый закат над горами"}'
```

```bash
{
  "positive": "beautiful sunset over mountains, vibrant orange and purple sky, majestic peaks, highly detailed, 4k, dramatic lighting",
  "negative": "low quality, blurry, distorted anatomy, extra limbs...",
  "input_text": "красивый закат над горами"
}
```

Переменные окружения
Вы можете переопределить параметры модели через .env файл:

HF_TOKEN	(обязательно)	Токен Hugging Face для скачивания модели
MODEL_PATH	/app/models/mistral-7b-instruct-v0.1.Q4_0.gguf	Путь к файлу модели внутри контейнера
LLAMA_N_CTX	2048	Размер контекста (токенов)
LLAMA_N_THREADS	4	Количество потоков CPU
LLAMA_VERBOSE	false	Логирование llama.cpp
FLASK_DEBUG	false	Режим отладки Flask (не включайте в продакшене)
