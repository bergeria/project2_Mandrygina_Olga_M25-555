# Здесь будет основная логика работы с таблицами и данными.



ALLOWED_TYPES = {"int", "str", "bool"}

def create_table( metadata: dict, table_name: str, columns: dict) -> None:
    """
    Добавляет таблицу в metadata.
    Автоматически добавляет столбец id:int.
    Проверяет корректность типов данных.
    """
    if table_name in metadata:
        raise ValueError(f"Таблица '{table_name}' уже существует")

    table_columns = {}

    # id всегда первый
    table_columns["id"] = "int"

    for column_name, column_type in columns.items():
        if column_name == "id":
            continue

        if column_type not in ALLOWED_TYPES:
            raise ValueError(
                f"Недопустимый тип данных '{column_type}' "
                f"для столбца '{column_name}'. "
                f"Допустимые типы: {', '.join(ALLOWED_TYPES)}"
            )

        table_columns[column_name] = column_type

    metadata[table_name] = {
        "columns": table_columns
    }

    #Типа создаем файл с таблицей ???
    #f_table_name = f"{table_name}.json"
    #save_metadata( f_table_name, metadata)


def drop_table(metadata: dict, table_name: str) -> None:
    """
    Удаляет таблицу из metadata.
    """
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")

    del metadata[table_name]


def list_tables(metadata: dict) -> list[str]:
    """
    Возвращает список всех таблиц из metadata.
    """
    return sorted(metadata.keys())



