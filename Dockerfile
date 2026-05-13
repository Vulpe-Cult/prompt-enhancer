FROM python:3.10-slim

# Установка только необходимых системных зависимостей
# llava-cpp-python имеет готовые бинарные колёса, компиляторы не нужны
RUN apt-get update && \
    apt-get install -y wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем только requirements.txt для кэширования слоя
COPY requirements.txt .

# Устанавливаем Python-зависимости (llama-cpp-python из готовых бинарных колёс)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Скрипт для скачивания модели при первом запуске (не во время сборки)
COPY download_model.py /app/download_model.py

# Открываем порт
EXPOSE 8001

# Запускаем сервер через entrypoint, который сначала проверит/скачает модель
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
