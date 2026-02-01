#Этот файл будет отвечать за запуск, игровой цикл и парсинг команд.

import shlex

import prompt
from core import create_table, drop_table, list_tables
from utils import load_metadata, save_metadata


# src/primitive_db/engine.py
def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n") 


def welcome ():
    pass


def parse_command( command_line: str) -> dict:
    tokens = shlex.split(command_line)

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
            return {
                "command": "list_tables"
            }

        # drop_table имя_таблицы
        case ["drop_table", table_name]:
            return {
                "command": "drop_table",
                "table_name": table_name,
            }

        # create_table без столбцов
        case ["create_table", *_]:
            raise ValueError(
                "Формат: create_table <имя_таблицы> <столбец:тип> [столбец:тип] ..."
            )

        case ["exit"]:
            return {
                "command": "exit"
            }

        case ["help"]:
            return {
                "command": "help"
            }
        # неизвестная команда
        case [command, *_]:
            raise ValueError(f"Неизвестная команда: {command}")


#Заготовка
def process_command( command : dict) -> None:
    pass


def run ():
    """Основной цикл"""

    c_line = ''

    while c_line != 'exit' :
        # Запрашиваем ввод у пользователя.
        c_line = prompt.string('Введите команду - ')

        try : # Разбирайте строку на команду и аргументы.
            command = parse_command( c_line)
        except ValueError as e :
            print(f"Ошибка в параметрах {e} !!!")
            continue

        # Загружаем метаданные
        metadata = load_metadata("db_meta.json")

        try :
            match command["command"]:
                case "create_table":
                    create_table(metadata,
                                 command["table_name"],
                                 command["columns"]
                    )
                    print(f' Таблица {command["table_name"]}\n'
                          f' со столбцами {command["columns"]}\n'
                          f' успешно создана\n')

                case "drop_table":
                    metadata = load_metadata("db_meta.json")
                    drop_table(metadata, command["table_name"])
                    print(f"Таблица - {command["table_name"]} - удалена\n")

                case "list_tables":
                    tables = list_tables( metadata)
                    if not tables:
                        print("Таблиц нет")
                    else:
                        for name in tables:
                            print(name)
                    continue

                case "help":
                    print_help()
                    continue

                case "exit":
                    break

                case _:
                    print("Команда не опознана !!!")
                    continue

        except ValueError as e:
            print(f"Ошибка -  {e}!!!")
            continue

        # Если не было исключений - сохраняем метаданные
        save_metadata("db_meta.json", metadata)







