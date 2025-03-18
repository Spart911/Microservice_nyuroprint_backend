# Используем официальный образ Python 3.12 в качестве базового
FROM python:3.12-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем требования в контейнер
COPY requirements.txt /app/

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в рабочую директорию контейнера
COPY . /app/

# Копируем файл .env в контейнер
COPY .env /app/

# Устанавливаем переменные окружения для работы с .env файлом
ENV PYTHONUNBUFFERED=1

# Открываем порт для FastAPI сервера
EXPOSE 8765

# Запуск сервера с помощью uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8765", "--workers", "4", "--ssl-keyfile", "/ssl/certificate.key.pem", "--ssl-certfile", "/ssl/certificate.crt.pem"]