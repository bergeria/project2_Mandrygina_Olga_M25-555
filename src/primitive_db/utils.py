# Для вспомогательных функций (например, работа с файлами).


import json
import os
import tempfile


def load_metadata(filepath: str) -> dict:
    """ Загружаем JSON файл"""

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {} # raise ValueError(f"Файл {filepath} содержит некорректный JSON")


def save_metadata(filepath: str, data: dict) -> None:
    dir_name = os.path.dirname(filepath) or "."

    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=dir_name,
        delete=False
    ) as tmp:
        json.dump(data, tmp, ensure_ascii=False, indent=4)
        temp_name = tmp.name

    os.replace(temp_name, filepath)
