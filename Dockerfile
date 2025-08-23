# Используем официальный образ Python 3.11
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Создаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем пользователя для запуска приложения (безопасность)
RUN adduser --disabled-password --gecos '' --uid 1000 botuser && \
    chown -R botuser:botuser /app
USER botuser

# Открываем порт (если понадобится для веб-хуков)
EXPOSE 8000

# Команда запуска
CMD ["python", "main.py"]

# Метки для документации
LABEL maintainer="HackerXAI" \
      description="Telegram Bot for Plant Recognition" \
      version="1.0.0"
