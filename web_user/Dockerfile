# Используем официальный Python образ
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем переменные окружения из .env
COPY .env /app/.env

# Открываем порт
EXPOSE 6004

# Команда для запуска бота
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "6004", "--workers", "4"]
