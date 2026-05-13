#!/bin/bash
set -e

# Скачиваем модель, если она отсутствует
if [ ! -f /app/models/mistral-7b-instruct-v0.1.Q4_0.gguf ]; then
    echo "Model not found, downloading..."
    python /app/download_model.py
fi

# Запускаем сервер
exec python -u enhance_server.py
