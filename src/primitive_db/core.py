# Здесь будет основная логика работы с таблицами и данными.


from typing import Any

from src.constants import ALLOWED_TYPES
from src.decorators import confirm_action, handle_db_errors, log_time
from src.primitive_db.utils import delete_table_data, load_table_data, save_table_data


@handle_db_errors
def _parse_value( raw: str, expected_type: str) -> Any:
    """ Преобразует строковое значение из команды в список типов.
    - expected_type: "int" | "str" | "bool"
    raw приходит уже распарсенным из shlex, но внутри values(...),
    """
    expected_type = expected_type.strip().lower()
    s = raw.strip()

    if expected_type == "int":
        # запрещаем пустое
        if s == "":
            raise ValueError("Пустое значение для int")
        try:
            return int(s)
        except ValueError:
            raise ValueError(f"Ожидался int, получено: {raw}")

    if expected_type == "bool":
        # поддержим true/false/1/0/yes/no
        v = s.lower()
        if v in ("true", "1", "yes", "y"):
            return True
        if v in ("false", "0", "no", "n"):
            return False
        raise ValueError(f"Ожидался bool (true/false), получено: {raw}")

    if expected_type == "str":
        # shlex обычно убирает кавычки, но если в values() остались,
        # то можно проверить и снять
        if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
            s = s[1:-1]
        return s

    raise ValueError(f"Неизвестный тип столбца: {expected_type}")

@handle_db_errors
@log_time
def insert(metadata: dict, table_name: str, values: list[str]) -> None:
    """
    metadata ожидается примерно такого вида:

    metadata = {
      "users": {
        "columns": {"ID": "int", "name": "str", "active": "bool"},
      }
    }

    values — список значений ИМЕННО ДЛЯ столбцов кроме ID, в порядке колонок metadata.
    """
    # Проверяем, существует ли таблица
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")

    # Список колонок таблицы
    table = metadata[table_name]

    if "columns" not in table or not isinstance(table["columns"], dict):
        raise ValueError(f"В таблице '{table_name}' нет схемы columns")

    # Берем названия и тип колонок таблицы
    columns = table["columns"]

    # Здесь порядок колонок должен быть всегда правильным

    # col_names - cписок названий колонок таблицы
    col_names = list(columns.keys())

    # количество колонок без ID
    non_id_cols = col_names[1:]

    # Проверка количества полученных значений и количество колонок без ID
    if len(values) != len(non_id_cols):
        raise ValueError(
            f"Ожидалось значений: {len(non_id_cols)} (без ID), получено: {len(values)}"
        )

    # Проверяем типы данных
    parsed_row: dict[str, Any] = {}
    for col_name, raw_val in zip(non_id_cols, values):
        expected_type = columns[col_name]
        parsed_row[col_name] = _parse_value(raw_val, expected_type)

    # Загружаем саму таблицу
    __data = load_table_data( table_name)

    # Генерируем новый ID
    max_id = 0
    for row in __data:
        if isinstance(row, dict) and "ID" in row:
            try:
                max_id = max(max_id, int(row["ID"]))
            except (TypeError, ValueError):
                raise ValueError(f"Некорректный ID в данных таблицы '{table_name}':"
                                 f" {row.get('ID')}")
    new_id = max_id + 1

    # Формируем запись целиком и добавляем
    new_record = {"ID": new_id, **parsed_row}
    __data.append( new_record)

    # Сохраняем саму таблицу
    save_table_data( table_name, __data)


@handle_db_errors
def _parse_value_for_type(raw: str, expected_type: str) -> Any:
    """ Разбираем параметры для select_from"""

    expected_type = expected_type.strip().lower()
    s = raw.strip()

    if expected_type == "int":
        if s == "":
            raise ValueError("Пустое значение для int")
        try:
            return int(s)
        except ValueError:
            raise ValueError(f"Ожидался int, получено: {raw}")

    if expected_type == "bool":
        v = s.lower()
        if v in ("true", "1", "yes", "y"):
            return True
        if v in ("false", "0", "no", "n"):
            return False
        raise ValueError(f"Ожидался bool (true/false), получено: {raw}")

    if expected_type == "str":
        # shlex обычно уже снял кавычки, но если они остались — снимем
        if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
            s = s[1:-1]
        return s

    raise ValueError(f"Неизвестный тип столбца: {expected_type}")


# Выборка select_from - теперь не используется
@handle_db_errors
@log_time
def select_from(metadata: dict, table_name: str,
                where: dict | None = None) -> list[dict]:
    """
    where:
      None  -> вернуть все записи
      {"column": "<col>", "value": "<raw_value>"} -> фильтр равенства

    Возвращает список словарей (строки таблицы).
    """
    # Проверяем наличие таблицы
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")

    table = metadata[table_name]

    # Берем схему столбцов
    columns = table.get("columns")
    if not isinstance(columns, dict) or not columns:
        raise ValueError(f"В таблице '{table_name}' некорректно описаны столбцы")

    # Загружаем саму таблицу
    data = load_table_data( table_name)

    if len(data) == 0:
        raise ValueError(f"В таблице '{table_name}' нет данных")

    # если без условия — вернуть все
    if where is None:
        return data # и уходим - вот только зачем воза

    # теперь разбираем условия where
    if not isinstance(where, dict) or "column" not in where or "value" not in where:
        raise ValueError("where должен быть вида: {'column': <col>, 'value': <value>}")

    col = where["column"]
    raw_val = where["value"]

    if col not in columns:
        raise ValueError(f"Столбца '{col}' нет в таблице '{table_name}'")

    # приводим значение к типу столбца
    expected_type = columns[col]
    typed_val = _parse_value_for_type(str(raw_val), expected_type)

    # фильтрация
    result: list[dict] = []
    for row in data:
        if not isinstance(row, dict):
            continue
        if row.get(col) == typed_val:
            result.append(row)

    return result


@handle_db_errors
@log_time
def select_from_cached(
    metadata: dict,
    table_name: str,
    where: dict | None,
    cache_result,
) -> list[dict]:
    """
    metadata[table_name] должен содержать:
      - "columns": dict
      - "data_file": путь к файлу с данными (например, data/users.json)

    cache_result — это функция, которую вернул create_cacher().
    """

    # Проверяем существует ли таблица
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")

    table = metadata[table_name]
    columns = table.get("columns")
    if not isinstance(columns, dict) or not columns:
        raise ValueError(f"В таблице '{table_name}' некорректно описаны столбцы")

    # строим ключ "select" при where=None
    if where is None:
        key = ("select", table_name, None, None)

        def compute():
            # читаем файл один раз на промахе
            data = load_table_data( table_name)
            # возвращаем данные
            return data

        return cache_result(key, compute)

    # строим ключ "select" при where != None
    if "column" not in where or "value" not in where:
        raise ValueError("where должен быть вида {'column': col, 'value': value}")

    col = where["column"]
    raw_val = where["value"]

    if col not in columns:
        raise ValueError(f"Столбца '{col}' нет в таблице '{table_name}'")

    typed_val = _parse_value_for_type(raw_val, columns[col])

    key = ("select", table_name, col, typed_val)

    def compute():
        data = load_table_data( table_name)
        result = [row for row in data if isinstance(row, dict)
                  and row.get(col) == typed_val]
        return result

    return cache_result(key, compute)

    # Конец select_from_cached

@handle_db_errors
def table_info( metadata: dict, table_name: str) -> None:
    """ Выводит информацию о таблице"""

    # Проверка существования таблицы
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")

    table = metadata[table_name]

    # Берем столбцы
    columns = table.get("columns")
    if not isinstance(columns, dict) or not columns:
        raise ValueError(f"В таблице '{table_name}' некорректно описаны столбцы")

    columns_str = ", ".join(f"{name}:{typ}" for name, typ in columns.items())

    # Загружаем саму таблицу
    __data = load_table_data( table_name)

    # Количество записей
    if not isinstance( __data, list):
        raise ValueError(f"В таблице '{table_name}' поле data должно быть списком")

    rows_count = len( __data)

    # Вывод информации
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns_str}")
    print(f"Количество записей: {rows_count}")


@handle_db_errors
def create_table( metadata: dict, table_name: str, columns: dict) -> None:
    """
    Добавляет таблицу в metadata.
    Автоматически добавляет столбец id:int.
    Проверяет корректность типов данных.
    """
    if table_name in metadata:
        raise ValueError(f"Таблица '{table_name}' уже существует")

    table_columns = {}

    # ID всегда первый
    table_columns["ID"] = "int"

    for column_name, column_type in columns.items():
        if column_name == "ID":
            continue

        if column_type not in ALLOWED_TYPES:
            raise ValueError(
                f"Недопустимый тип данных '{column_type}' "
                f"для столбца '{column_name}'. "
                f"Допустимые типы: {', '.join(ALLOWED_TYPES)}"
            )

        table_columns[column_name] = column_type

    metadata[table_name] = {"columns": table_columns}
    print(f' Таблица {table_name} - успешно создана\n')


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> None:
    """
    Удаляет таблицу из metadata.
    """
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")

    del metadata[table_name]
    delete_table_data(table_name)
    print(f"Таблица - {table_name} - удалена\n")


def list_tables(metadata: dict) -> list[str]:
    """
    Возвращает список всех таблиц из metadata.
    """
    return sorted(metadata.keys())


# Изменяем значения в таблице
@handle_db_errors
@log_time
def update_table(
    metadata: dict,
    table_name: str,
    set_values: dict,
    where: dict,
) -> list[dict]:
    """
    set_values: {"age": "29"}
    where: {"column": "name", "value": "Sergei"}

    Возвращает количество обновлённых записей.
    """
    # Проверяем наличие таблицы
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")

    # Список столбцов
    table = metadata[table_name]

    # Берем схему столбцов
    columns = table.get("columns")
    if not isinstance(columns, dict):
        raise ValueError(f"В таблице '{table_name}' нет описания столбцов")

    # Проверяем наличие where
    if "column" not in where or "value" not in where:
        raise ValueError("where должен быть вида {'column': col, 'value': value}")

    where_col = where["column"]
    where_raw_val = where["value"]

    if where_col not in columns:
        raise ValueError(f"Столбца '{where_col}' нет в таблице '{table_name}'")

    where_val = _parse_value_for_type(where_raw_val, columns[where_col])

    # Проверка set
    if not set_values:
        raise ValueError("set не может быть пустым")

    # Разбираем set - вроде как их может быть несколько
    parsed_set: dict[str, Any] = {}
    for col, raw_val in set_values.items():
        if col not in columns:
            raise ValueError(f"Столбца '{col}' нет в таблице '{table_name}'")
        if col == "ID":
            raise ValueError("Нельзя изменять ID")
        parsed_set[col] = _parse_value_for_type(raw_val, columns[col])

    # Загружаем саму таблицу из файла
    data = load_table_data( table_name)

    if not isinstance(data, list):
        raise ValueError(f"В таблице '{table_name}' поле data должно быть списком")

    # Пробуем обновить
    updated_list = []

    for row in data:
        if not isinstance(row, dict):
            continue
        if row.get(where_col) != where_val:
            continue
        for col, val in parsed_set.items():
            row[col] = val
            updated_list.append( row)

    # Сохраняем саму таблицу в файл
    save_table_data( table_name, data)

    # Возвращаем список измененных записей
    return updated_list

# Удаляем сроки по условию
@handle_db_errors
@confirm_action("удаление записей")
@log_time
def delete_from( metadata : dict, table_name: str, where: dict) -> list[dict] :
    """
    where = {"column": "<col>", "value": "<raw_value>"}
    Возвращает количество удалённых записей.
    """
    # Проверяем наличие таблицы
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")

    table = metadata[table_name]

    # Берем схему столбцов
    columns = table.get("columns")
    if not isinstance(columns, dict) or not columns:
        raise ValueError(f"В таблице '{table_name}' некорректно описаны столбцы")

    # Проверяем наличие where
    if not isinstance(where, dict) or "column" not in where or "value" not in where:
        raise ValueError("where должен быть вида: {'column': <col>, 'value': <value>}")

    col = where["column"]
    raw_val = where["value"]

    if col not in columns:
        raise ValueError(f"Столбца '{col}' нет в таблице '{table_name}'")

    typed_val = _parse_value_for_type(raw_val, columns[col])

    # Читаем данные из файла
    data = load_table_data( table_name)

    if data is None:
        raise ValueError(f"В таблице '{table_name}' нет данных !!!")

    if not isinstance(data, list):
        raise ValueError(f"В таблице '{table_name}' поле data должно быть списком")

    # Начинаем удаление
    new_table = []
    del_list = []
    for row in data :
        if not ( isinstance(row, dict)) :
            continue
        if row.get(col) != typed_val :
            new_table.append(row)
        else:
            del_list.append(row)

    #result = [r for r in data if r[col] != typed_val]

    # Сохраняем новую таблицу в файл
    save_table_data( table_name, new_table)

    #Возвращаем список удаленных записей
    return del_list


