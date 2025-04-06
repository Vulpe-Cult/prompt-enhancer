# Prompt Enhancer for Stable Diffusion

Системные требования
Docker 20.10+ и Docker Compose 1.29+
Память: Минимум 4GB RAM (8GB+ рекомендовано для работы модели)
Диск: 10GB+ свободного места (для хранения моделей)

Обязательные параметры
# .env файл должен содержать:
HF_TOKEN=your_huggingface_token_here  # Токен API Hugging Face

Зависимости
Компонент	Версия	Назначение
Python	3.10+	Базовый интерпретатор
llama-cpp-python	≥0.2.0	Работа с GGUF-моделями
Flask	≥2.3.0	Веб-сервер API
requests	≥2.31.0	HTTP-запросы


Микросервис для преобразования русских описаний в промпты для Stable Diffusion.

## Установка

1. Создайте `.env` файл:
```bash
echo "HF_TOKEN=ваш_токен" > .env
```
2. Запустите:
```bash
docker compose up --build
```

## Использование
```bash
curl -X POST http://localhost:8001/enhance \
  -H "Content-Type: application/json" \
  -d '{"text":"описание"}'
```
