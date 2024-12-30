import pika
import numpy as np
import json
from sklearn.datasets import load_diabetes
from datetime import datetime
import time

# Создаём бесконечный цикл для отправки сообщений в очередь
while True:
    try:
        # Загружаем датасет о диабете
        X, y = load_diabetes(return_X_y=True)
        # Формируем случайный индекс строки
        random_row = np.random.randint(0, X.shape[0] - 1)

        # Попытка подключения к RabbitMQ
        print("Попытка подключения к RabbitMQ...")
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        # Создаём очередь y_true
        channel.queue_declare(queue='y_true')
        # Создаём очередь features
        channel.queue_declare(queue='features')

        # Генерируем уникальный идентификатор сообщения
        message_id = datetime.timestamp(datetime.now())

        # Создаём сообщение для y_true
        message_y_true = {
            'id': message_id,
            'body': y[random_row]
        }
        # Публикуем сообщение в очередь y_true
        channel.basic_publish(
            exchange='',
            routing_key='y_true',
            body=json.dumps(message_y_true)
        )
        print(f'Сообщение с правильным ответом отправлено в очередь: {message_y_true}')

        # Создаём сообщение для features
        message_features = {
            'id': message_id,
            'body': list(X[random_row])
        }
        # Публикуем сообщение в очередь features
        channel.basic_publish(
            exchange='',
            routing_key='features',
            body=json.dumps(message_features)
        )
        print(f'Сообщение с вектором признаков отправлено в очередь: {message_features}')

        # Закрываем подключение
        connection.close()

        # Задержка перед следующей итерацией
        time.sleep(5)  # Задержка в 5 секунд
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Ошибка подключения к RabbitMQ: {e}. Повторная попытка через 5 секунд...")
        time.sleep(5)  # Ждём перед повторной попыткой
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
