import pika
import json
import pandas as pd
import os
import time

# Определяем путь к папке logs (на одном уровне с src)
LOGS_DIR = "/metric/logs"
LOG_FILE = os.path.join(LOGS_DIR, "metric_log.csv")

print("Абсолютный путь к папке logs:", os.path.abspath(LOGS_DIR))
print("Абсолютный путь к файлу log:", os.path.abspath(LOG_FILE))

# Убедимся, что папка logs существует
os.makedirs(LOGS_DIR, exist_ok=True)

# Инициализируем CSV-файл, если его нет
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=['id', 'y_true', 'y_pred', 'absolute_error']).to_csv(LOG_FILE, index=False)

# Хранилище для сообщений
message_storage = {}

# Функция подключения к RabbitMQ с повторными попытками
def connect_to_rabbitmq():
    while True:
        try:
            print("Попытка подключения к RabbitMQ...")
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            print("Успешное подключение к RabbitMQ")
            return connection
        except Exception as e:
            print(f"Ошибка подключения к RabbitMQ: {e}. Повторная попытка через 5 секунд...")
            time.sleep(5)

# Подключение к RabbitMQ
connection = connect_to_rabbitmq()
channel = connection.channel()

# Объявляем очереди y_true и y_pred
channel.queue_declare(queue='y_true')
channel.queue_declare(queue='y_pred')

# Обработка данных из очереди y_true
def callback_y_true(ch, method, properties, body):
    try:
        print(f"Получено сообщение y_pred: {body}")
        data = json.loads(body)
        if 'id' not in data or 'body' not in data:
            raise ValueError("Сообщение должно содержать поля 'id' и 'body'")
        message_id = data['id']
        y_true = data['body']

        # Сохраняем данные в хранилище
        if message_id not in message_storage:
            message_storage[message_id] = {}
        message_storage[message_id]['y_true'] = y_true

        # Проверяем, можно ли вычислить ошибку
        calculate_and_log(message_id)
    except Exception as e:
        print(f"Ошибка обработки сообщения y_true: {e}")

# Обработка данных из очереди y_pred
def callback_y_pred(ch, method, properties, body):
    try:
        print(f"Получено сообщение y_pred: {body}")
        data = json.loads(body)
        if 'id' not in data or 'body' not in data:
            raise ValueError("Сообщение должно содержать поля 'id' и 'body'")
        message_id = data['id']
        y_pred = data['body']

        # Сохраняем данные в хранилище
        if message_id not in message_storage:
            message_storage[message_id] = {}
        message_storage[message_id]['y_pred'] = y_pred

        # Проверяем, можно ли вычислить ошибку
        calculate_and_log(message_id)
    except Exception as e:
        print(f"Ошибка обработки сообщения y_pred: {e}")

# Вычисление ошибки и запись в лог
def calculate_and_log(message_id):
    try:
        if 'y_true' in message_storage[message_id] and 'y_pred' in message_storage[message_id]:
            y_true = message_storage[message_id]['y_true']
            y_pred = message_storage[message_id]['y_pred']
            absolute_error = abs(y_true - y_pred)

            # Логируем данные
            log_data = {
                'id': message_id,
                'y_true': y_true,
                'y_pred': y_pred,
                'absolute_error': absolute_error
            }
            print(f"Логирование данных: {log_data}")
            df = pd.DataFrame([log_data])

            # Проверяем, существует ли файл
            if os.path.exists(LOG_FILE):
                # Если файл существует, добавляем данные без заголовков
                df.to_csv(LOG_FILE, mode='a', header=False, index=False)
            else:
                # Если файл не существует, создаём с заголовками
                df.to_csv(LOG_FILE, mode='w', header=True, index=False)

            # Удаляем обработанное сообщение из хранилища
            del message_storage[message_id]
    except Exception as e:
        print(f"Ошибка логирования данных: {e}")

# Извлекаем сообщение из очереди y_true
channel.basic_consume(
    queue='y_true',
    on_message_callback=callback_y_true,
    auto_ack=True
)

# Извлекаем сообщение из очереди y_pred
channel.basic_consume(
    queue='y_pred',
    on_message_callback=callback_y_pred,
    auto_ack=True
)

# Запускаем режим ожидания прихода сообщений
print('...Ожидание сообщений, для выхода нажмите CTRL+C')
try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Остановка потребления сообщений")
    channel.stop_consuming()
    connection.close()