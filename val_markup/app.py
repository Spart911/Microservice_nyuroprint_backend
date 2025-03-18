import requests
import pandas as pd
import time
import os
import json
import logging
from collections import defaultdict
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# URL API
URL = os.getenv("URL")
BONUSES_API_BASE = os.getenv("BONUSES_API_BASE")  # Базовый URL API для бонусов
CSV_FILE = os.getenv("CSV_FILE")
STATE_FILE = os.getenv("STATE_FILE")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL"))  # Интервал проверки в секундах

# Настроим логирование
logging.basicConfig(
    filename="sync_bonuses.log",  # Указываем файл для логов
    level=logging.INFO,           # Уровень логирования
    format="%(asctime)s - %(levelname)s - %(message)s",  # Формат сообщений
    datefmt="%Y-%m-%d %H:%M:%S"   # Формат времени
)

# Функция загрузки состояния
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                logging.error("Ошибка: файл состояния повреждён. Пересоздаём его.")
                return {"last_processed_id": 0}
    return {"last_processed_id": 0}


# Функция сохранения состояния
def save_state(state):
    with open(STATE_FILE, "w") as file:
        json.dump(state, file)


# Загружаем последнее обработанное состояние
state = load_state()


def fetch_csv():
    logging.info("Запрашиваю CSV файл с данными...")
    response = requests.get(URL, verify=False)
    if response.status_code == 200:
        with open(CSV_FILE, "wb") as file:
            file.write(response.content)
        logging.info("CSV файл успешно загружен.")
        return True
    else:
        logging.error(f"Ошибка при запросе данных: {response.status_code}")
        return False


def get_user_bonuses(user_id):
    """
    Получает текущее количество бонусов пользователя через API
    """
    logging.info(f"Запрашиваю текущее количество бонусов для пользователя {user_id}...")
    url = f"{BONUSES_API_BASE}/users/telegram/{user_id}/bonuses"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            bonuses = response.json()
            logging.info(f"Текущее количество бонусов пользователя {user_id}: {bonuses}")
            return bonuses
        else:
            logging.error(f"Ошибка при запросе бонусов пользователя {user_id}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"Исключение при запросе бонусов пользователя {user_id}: {str(e)}")
        return None


def set_user_bonuses(user_id, amount):
    """
    Устанавливает новое количество бонусов пользователя через API
    """
    logging.info(f"Устанавливаю новое количество бонусов для пользователя {user_id}: {amount}...")
    url = f"{BONUSES_API_BASE}/users/telegram/{user_id}/set-bonuses"
    params = {"amount": amount}
    try:
        response = requests.put(url, params=params)
        if response.status_code == 200:
            logging.info(f"Количество бонусов для пользователя {user_id} успешно обновлено до {amount}")
            return True
        else:
            logging.error(f"Ошибка при обновлении бонусов пользователя {user_id}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logging.error(f"Исключение при обновлении бонусов пользователя {user_id}: {str(e)}")
        return False


def process_csv():
    global state
    logging.info("Начинаю обработку CSV файла...")
    df = pd.read_csv(CSV_FILE)
    df = df[df['id'] > state['last_processed_id']]  # Убираем старые данные

    if df.empty:
        logging.info("Нет новых данных для обработки.")
        return

    logging.info(f"Найдено {len(df)} новых записей для обработки.")
    state['last_processed_id'] = int(df['id'].max())  # Приводим к int
    save_state(state)
    logging.info(f"Обновлено последнее обработанное ID: {state['last_processed_id']}")

    user_valid_counts = defaultdict(int)

    # Обработка для каждого пользователя
    unique_users = df['userUid'].str.split('_').str[0].unique()
    logging.info(f"Найдено {len(unique_users)} уникальных пользователей для обработки.")

    for user_uid in unique_users:
        logging.info(f"Обрабатываю данные пользователя {user_uid}...")
        # Получаем все строки для этого пользователя (включая с _val)
        user_all_rows = df[df['userUid'].str.startswith(user_uid)]

        if user_all_rows.empty:
            logging.warning(f"Нет данных для пользователя {user_uid}, пропускаю.")
            continue

        # Сортируем по id для обеспечения правильного порядка
        user_all_rows = user_all_rows.sort_values('id')
        logging.info(f"Найдено {len(user_all_rows)} записей для пользователя {user_uid}.")

        segments = []
        current_segment = []
        in_segment = False
        last_val_row = None

        logging.info(f"Анализирую сегменты записей пользователя {user_uid}...")
        for idx, row in user_all_rows.iterrows():
            if row['userUid'].endswith('_val'):
                # Встретили _val запись
                if in_segment and current_segment:
                    # Если уже были в сегменте, закрываем его
                    segments.append({
                        'rows': current_segment,
                        'next_val_row': row  # Сохраняем следующую _val запись
                    })
                    logging.info(f"Сформирован сегмент из {len(current_segment)} записей.")
                    current_segment = []
                last_val_row = row
                in_segment = True  # Следующие записи будут в сегменте
                logging.info(f"Обнаружена валидационная запись: {row['userUid']}")
            elif in_segment:
                # Не _val запись и мы внутри сегмента
                current_segment.append(row)
                logging.info(f"Добавлена запись в текущий сегмент: {row['userUid']}")

        logging.info(f"Всего найдено {len(segments)} сегментов для пользователя {user_uid}.")

        # Фильтруем сегменты по условию валидации
        valid_segments = []
        for i, segment in enumerate(segments):
            next_val_row = segment['next_val_row']
            logging.info(f"Проверяю валидность сегмента {i + 1}...")

            # Проверяем, сколько False значений в следующей _val записи
            # Получаем значения, начиная с 4-го столбца (индекс 3)
            val_values = next_val_row.iloc[3:].values

            # Считаем количество False
            false_count = sum(1 for val in val_values if val == False)
            logging.info(f"Найдено {false_count} невалидных значений в валидационной записи.")

            # Если меньше 3 False, считаем сегмент валидным
            if false_count < 3:
                valid_segments.append(segment['rows'])
                logging.info(f"Сегмент {i + 1} признан валидным.")
            else:
                logging.info(f"Сегмент {i + 1} признан невалидным (больше 2 невалидных значений).")

        # Подсчет валидных записей для пользователя
        valid_count = sum(len(segment) for segment in valid_segments)
        if valid_count > 0:
            user_valid_counts[user_uid] += valid_count
            logging.info(f"Итого для пользователя {user_uid}: найдено {valid_count} валидных записей.")

    logging.info("\nРезультаты обработки:")
    for user, count in user_valid_counts.items():
        logging.info(f"Пользователь {user}: {count} валидных записей")

        # Теперь сравним с текущими бонусами и обновим при необходимости
        current_bonuses = get_user_bonuses(user)



        if current_bonuses is not None:
            difference = current_bonuses - count
            if difference != 0:
                logging.info(f"Расхождение для пользователя {user}: {difference} (текущие бонусы: {current_bonuses}, валидные записи: {count})")

                # Обновляем количество бонусов
                if set_user_bonuses(user, count):
                    logging.info(f"Бонусы пользователя {user} успешно обновлены с {current_bonuses} на {count}")
                else:
                    logging.error(f"Не удалось обновить бонусы пользователя {user}")
            else:
                logging.info(f"Количество бонусов пользователя {user} уже соответствует количеству валидных записей ({count})")
        else:
            logging.error(f"Не удалось получить текущие бонусы пользователя {user}")


def main():
    logging.info("Запуск программы синхронизации бонусов...")
    while True:
        logging.info("\n--- Начало нового цикла проверки ---")
        logging.info(f"Время: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        if fetch_csv():
            process_csv()
        else:
            logging.error("Пропуск обработки из-за ошибки загрузки данных.")

        logging.info(f"Следующая проверка через {CHECK_INTERVAL} секунд.")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
