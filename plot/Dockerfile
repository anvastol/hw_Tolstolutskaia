# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /src

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем скрипт
COPY src/plot.py ./plot.py

# Запускаем скрипт
CMD ["python", "plot.py"]
