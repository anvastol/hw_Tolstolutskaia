import pika
import pickle
import numpy as np
import json
import time

# Читаем файл с сериализованной моделью
try:
    with open('./src/myfile.pkl', 'rb') as pkl_file:
        regressor = pickle.load(pkl_file)
    print("Модель успешно загружена.")
except FileNotFoundError:
    print("Файл myfile.pkl не найден.")
    exit(1)
except Exception as e:
    print(f"Ошибка при загрузке модели: {e}")
    exit(1)

# Повторное подключение к RabbitMQ
while True:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
        print("Успешное подключение к RabbitMQ.")
        break
    except Exception as e:
        print(f"Ошибка подключения к RabbitMQ: {e}. Повторная попытка через 5 секунд...")
        time.sleep(5)

# Объявляем очереди
channel.queue_declare(queue='features')
channel.queue_declare(queue='y_pred')

# Callback для обработки сообщений
def callback(ch, method, properties, body):
    try:
        # Декодируем сообщение и парсим JSON
        data = json.loads(body.decode('utf-8'))
        print(f"Получен вектор признаков {data}")

        # Извлечение признаков
        message_id = data["id"]
        features = data["body"]

        # Убедимся, что признаки - это список
        if not isinstance(features, list):
            raise ValueError("Полученные признаки должны быть списком")

        # Выполнение предсказания
        pred = regressor.predict(np.array(features).reshape(1, -1))
        # Публикация результата в RabbitMQ
        channel.basic_publish(
            exchange='',
            routing_key='y_pred',
            body=json.dumps({"id": message_id, "body": pred[0]})
        )
        print(f"Предсказание {pred[0]} отправлено в очередь y_pred")
    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")

# Подключаем callback к очереди
channel.basic_consume(
    queue='features',
    on_message_callback=callback,
    auto_ack=True
)

# Ожидание сообщений
print('...Ожидание сообщений, для выхода нажмите CTRL+C')
try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Завершение работы")
    connection.close()