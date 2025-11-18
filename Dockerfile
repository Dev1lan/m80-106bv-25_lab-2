FROM python:3.11-slim

LABEL maintainer="Dev1lan"
LABEL version="1.0.0"
LABEL description="Mini shell with file commands"

WORKDIR /app

# Устанавливаем системные зависимости для opencv
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем только необходимые Python зависимости
RUN pip install --no-cache-dir \
    opencv-python==4.12.0.88 \
    Pygments==2.19.2

# Копируем исходный код
COPY src/ ./src/
COPY pyproject.toml .
COPY README.md .

# Создаем директорию для данных
RUN mkdir /data

WORKDIR /data

ENTRYPOINT ["python", "/app/src/main.py"]
