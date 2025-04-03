FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y wget git cmake g++ && \
    # Очистка кеша apt
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Установка Python-зависимостей
RUN pip install --no-cache-dir \
    llama-cpp-python \
    flask \
    requests \
    python-dotenv

# Установка llama.cpp
RUN git clone https://github.com/ggerganov/llama.cpp.git /llama.cpp && \
    cd /llama.cpp && \
    mkdir build && \
    cd build && \
    cmake .. && \
    cmake --build . --config Release

# Создаем рабочую директорию
WORKDIR /app

# Копируем сначала только requirements.txt для кэширования
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы
COPY . .

# Скачиваем модель (с проверкой наличия токена)
ARG HF_TOKEN
RUN if [ -z "${HF_TOKEN}" ]; then \
        echo "Error: HF_TOKEN not provided"; \
        exit 1; \
    else \
        mkdir -p /app/models && \
        wget --header="Authorization: Bearer ${HF_TOKEN}" \
             -O /app/models/mistral-7b-instruct-v0.1.Q4_0.gguf \
             https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_0.gguf || exit 1; \
    fi

EXPOSE 8001
CMD ["python", "-u", "enhance_server.py"]
