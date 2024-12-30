# Подключаем базовый образ Python 3.9
FROM python:3.9-slim

# Задаем рабочую директорию контейнера
WORKDIR /src

# Копируем содержимое папки src в рабочую директорию
COPY ./src ./src

# Копируем файл с зависимостями в рабочую директорию
COPY requirements.txt .

# Копируем модельный файл в рабочую директорию
COPY ./src/myfile.pkl ./src

# Устанавливаем все необходимые зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем скрипт для работы сервиса
CMD ["python", "./src/model.py"]
