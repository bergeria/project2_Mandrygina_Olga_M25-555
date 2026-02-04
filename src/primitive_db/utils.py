# Для вспомогательных функций (например, работа с файлами).


import json
import os
import tempfile

from prettytable import PrettyTable

from src.constants import DATA_DIR


def delete_table_data( table_name :str) :
    """ Удаляем JSON файл таблицы"""
    # Берем текущую рабочую директорию +
    c_path = os.getcwd()
    # имя файла -> Целевой файл с данными таблицы
    filepath = os.path.join(c_path, DATA_DIR, table_name+".json")
    if os.path.exists( filepath):  # если файл есть
        os.remove( filepath)


def load_table_data( table_name :str) -> list:
    """ Загружаем таблицу из JSON файла"""

    # Берем текущую рабочую директорию +
    c_path = os.getcwd()
    # имя файла -> Целевой файл с данными таблицы
    filepath = os.path.join(c_path, DATA_DIR, table_name+".json")

    try:
        with open( filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return [] # raise ValueError(f"Файл {filepath} содержит некорректный JSON")


def save_table_data( table_name:str, data:list):
    """ Записываем файл таблицы в JSON файл"""

    # Берем текущую рабочую директорию +
    c_path = os.getcwd()
    #Пусь к имени файла
    dir_name = os.path.join( c_path, DATA_DIR)
    # имя файла -> Целевой файл с данными таблицы
    filepath = os.path.join( dir_name, table_name+".json")

    with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=dir_name,
            delete=False
    ) as tmp:
        json.dump( data, tmp, ensure_ascii=False, indent=4)
        temp_name = tmp.name

    os.replace( temp_name, filepath)


def load_metadata( filepath: str) -> dict:
    """ Загружаем список таблиц из JSON файла"""

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {} # raise ValueError(f"Файл {filepath} содержит некорректный JSON")


def save_metadata( filepath: str, data: dict) -> None:
    """ Сохраняет список таблиц в формате JSON"""

    dir_name = os.path.dirname(filepath) or "."

    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=dir_name,
        delete=False
    ) as tmp:
        json.dump(data, tmp, ensure_ascii=False, indent=4)
        temp_name = tmp.name

    os.replace( temp_name, filepath)


# Вывод информации в виде таблицы
def print_list( rows: list[dict]) -> None:
    if not rows:
        print("Нет данных")
        return

    # Берём порядок колонок из первого словаря
    columns = list(rows[0].keys())

    table = PrettyTable()
    table.field_names = columns

    for row in rows:
        # гарантируем порядок значений
        table.add_row([row.get(col) for col in columns])

    print( table)

