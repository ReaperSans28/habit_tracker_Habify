FROM python:3.13-slim
WORKDIR /app
# Если будем выгружать на вдску (Выгружу если нужно)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    sqlite3 \
 && rm -rf /var/lib/apt/lists/*
# Тут зависимости качаем
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Ускоряем вывод логов
ENV PYTHONUNBUFFERED=1
# Проверяем, что бот жив
HEALTHCHECK CMD pgrep -f "python main.py" > /dev/null || exit 1
# Запускаем бота
CMD ["python", "main.py"]

