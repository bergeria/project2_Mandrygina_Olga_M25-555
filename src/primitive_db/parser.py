# Модуль разбора команд

import shlex


def _parse_parenthesized_values(tokens: list[str]) -> list[str]:
    """
    Ожидает токены вида: ['(', v1, ',', v2, ',', ..., ')']
    Возвращает список значений [v1, v2, ...] (как строки, shlex уже снял кавычки).
    """
    if not tokens or tokens[0] != "(" or tokens[-1] != ")":
        raise ValueError("Ожидались скобки: ( ... )")

    inner = tokens[1:-1]
    if not inner:
        return []

    values: list[str] = []
    current: list[str] = []

    for t in inner:
        if t == ",":
            if not current:
                raise ValueError("Пустое значение между запятыми")
            values.append(" ".join(current).strip())
            current = []
        else:
            current.append(t)

    if not current:
        raise ValueError("Пустое значение в конце списка")
    values.append(" ".join(current).strip())

    return values


def normalize_sql_like_input(s: str) -> str:
    for ch in ("(", ")", ",","="):
        s = s.replace(ch, f" {ch} ")
    return s


def parse_command(command_line: str) -> dict:

    # раздвигаем скобки, запятые и = - добавляем пробелы
    normalized = normalize_sql_like_input( command_line)
    tokens = shlex.split(normalized)

    if not tokens:
        raise ValueError("Пустая команда")

    match tokens:
        # create_table имя_таблицы col:type col:type ...
        case ["create_table", table_name, *cols] if cols:
            columns = {}
            for col in cols:
                if ":" not in col:
                    raise ValueError(f"Неверное описание столбца: {col}")
                name, col_type = col.split(":", 1)
                columns[name] = col_type

            return {
                "command": "create_table",
                "table_name": table_name,
                "columns": columns,
            }

        # list_tables
        case ["list_tables"]:
            return {"command": "list_tables"}

        # drop_table имя_таблицы
        case ["drop_table", table_name]:
            return {"command": "drop_table", "table_name": table_name}

        # info имя_таблицы - вывести информацию о таблице.
        case ["info", table_name]:
            return {"command": "info", "table_name": table_name}

        # insert into table_name values ( v1, v2, ... )
        # пример: insert into users values ( 1, "Test", true )
        case ["insert", "into", table_name, "values", *rest]:
            values = _parse_parenthesized_values(rest)
            return {
                "command": "insert",
                "table_name": table_name,
                "values": values,
            }

        # select from table_name
        case ["select", "from", table_name]:
            return {
                "command": "select",
                "table_name": table_name,
                "where": None,
            }

        # select from table_name where col = value
        case ["select", "from", table_name, "where", col, "=", value]:
            return {
                "command": "select",
                "table_name": table_name,
                "where": {"column": col, "value": value},
            }

        # delete from table_name where col = value
        case ["delete", "from", table_name, "where", col, "=", value]:
            return {
                "command": "delete",
                "table_name": table_name,
                "where": {"column": col, "value": value},
            }

        # update table_name set col1 = v1 where col2 = v2
        # Поддержка нескольких set - может и не получилось...
        case ["update", table_name, "set", set_col, "=", set_val,
              "where", where_col, "=", where_val]:
            return {
                "command": "update",
                "table_name": table_name,
                "set": {set_col: set_val},
                "where": {"column": where_col, "value": where_val},
            }

        # create_table без столбцов
        case ["create_table", *_]:
            raise ValueError(
                "Формат: create_table <имя_таблицы> <столбец:тип> [столбец:тип] ..."
            )

        case ["exit"]:
            return {"command": "exit"}

        case ["help"]:
            return {"command": "help"}

        # неизвестная команда
        case [command, *_]:
            raise ValueError(f"Неизвестная команда: {command} "
                             f"- или ошибка в параметрах")
