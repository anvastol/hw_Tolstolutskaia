import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import time

# Указываем путь к папке logs в metric
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../metric/logs"))
LOG_FILE = os.path.join(BASE_DIR, "metric_log.csv")
PLOT_FILE = os.path.join(BASE_DIR, "error_distribution.png")

# Убедимся, что файл с логами существует
if not os.path.exists(LOG_FILE):
    print(f"Файл {LOG_FILE} не найден. Ожидание создания файла...")
    while not os.path.exists(LOG_FILE):
        time.sleep(5)

# Бесконечный цикл для обновления графика
while True:
    try:
        # Загружаем данные
        df = pd.read_csv(LOG_FILE)
        if df.empty:
            print("Файл metric_log.csv пуст. Ожидание новых данных...")
            time.sleep(5)
            continue

        # Создаём график
        sns.histplot(df['absolute_error'], kde=True, color='orange')
        plt.title("Распределение абсолютных ошибок")
        plt.xlabel("absolute_error")
        plt.ylabel("Count")

        # Сохраняем график
        plt.savefig(PLOT_FILE)
        plt.close()
        print(f"График сохранён в {PLOT_FILE}")

        # Задержка перед обновлением
        time.sleep(10)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(10)