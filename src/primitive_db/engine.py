#Этот файл будет отвечать за запуск, игровой цикл и парсинг команд.

import os
from typing import Any, Callable

import prompt

from src.constants import COMMANDS, DATA_DIR, METADATA_JSON
from src.primitive_db.core import (
    create_table,
    delete_from,
    drop_table,
    insert,
    list_tables,
    select_from_cached,
    table_info,
    update_table,
)
from src.primitive_db.parser import parse_command
from src.primitive_db.utils import load_metadata, print_list, save_metadata


# src/primitive_db/engine.py
def print_help():
    """Prints the help message for the current mode."""
    for help_str in COMMANDS:
        print(help_str)


def create_cacher():
    """
    Возвращает функцию cache_result(key, value_func),
    у которой есть метод clear().
    """
    cache: dict[Any, Any] = {}

    def cache_result(key: Any, value_func: Callable[[], Any]) -> Any:
        if key in cache:
            return cache[key]

        value = value_func()
        cache[key] = value
        return value

    def clear(prefix: Any | None = None) -> None:
        """
        clear()              -> очистить весь кэш
        clear(prefix)        -> очистить записи, ключи которых начинаются с prefix
                                (например, prefix=("select", "users"))
        """
        nonlocal cache

        if prefix is None:
            cache.clear()
            return

        keys_to_delete = [k for k in cache if isinstance(k, tuple)
                          and k[:len(prefix)] == prefix]
        for k in keys_to_delete:
            del cache[k]

    # "прикручиваем" метод к функции
    cache_result.clear = clear

    return cache_result

    # Конец create_cacher


def run ():
    """Основной цикл"""

    c_line = ''
    cache_result = create_cacher()

    meta_file = os.path.join( os.getcwd(), DATA_DIR, METADATA_JSON)

    while c_line != 'exit' :
        # Запрашиваем ввод у пользователя.
        c_line = prompt.string('\nВведите команду - ')

        try : # Разбирайте строку на команду и аргументы.
            command = parse_command( c_line)
        except ValueError as e :
            print(f"Ошибка - {e} !!!")
            continue

        # Загружаем метаданные
        metadata = load_metadata( meta_file)

        match command["command"]:
            case "create_table":
                # Изменяем состав db_meta.json
                create_table(metadata,
                             command["table_name"],
                             command["columns"]
                )
                # сохраняем метаданные. Если не было исключений ???
                # хотя исключения суда не дойдут - они теперь обрабатываются раньше
                save_metadata( meta_file, metadata)

            case "drop_table":
                # Удаляем таблицу - изменяем состав db_meta.json, удаляем файл
                drop_table(metadata, command["table_name"])
                # сохраняем метаданные. Если не было исключений ???
                # хотя исключения суда не дойдут - они теперь обрабатываются раньше
                save_metadata( meta_file, metadata)
                # Очищаем кеш
                cache_result.clear( ("select", command["table_name"]))

            case "list_tables": # list_tables - вывести список таблиц
                tables = list_tables( metadata)
                if not tables:
                    print("Таблиц нет")
                else:
                    for name in tables:
                        print(name)

            case "insert":
                # insert Изменяем состав таблицы
                insert( metadata, command["table_name"], command["values"])
                # Очищаем кеш
                cache_result.clear( ("select", command["table_name"]))

            case "info": # info имя_таблицы - вывести информацию о таблице
                table_info( metadata, command["table_name"])

            case "select": # select делаем выборку из таблицы
#                s_from = select_from( metadata,
#                                    command["table_name"],
#                                    command["where"])
                s_form = select_from_cached( metadata,
                                             command["table_name"],
                                             command["where"],
                                             cache_result)
                # Выводим результат
                print_list( s_form)

            case "update":
                # update Изменяем состав таблицы
                change_list = update_table( metadata,
                                            command["table_name"],
                                            command["set"],
                                            command["where"])
                if len(change_list) == 0 or change_list is None:
                    print(f'Записи с условием {command["where"]}'
                          f' - не найдены !!!')
                    continue
                print( f'\nСписок измененных записей по условию '
                       f'{command["where"]}\n -')
                # Очищаем кеш
                cache_result.clear( ("select", command["table_name"]))
                print_list( change_list)

            case "delete":
                # delete Изменяем состав таблицы
                deleted_list = delete_from( metadata,
                                            command["table_name"],
                                            command["where"])
                if len(deleted_list) == 0 or deleted_list is None :
                    print(f'Записи с условием {command["where"]}'
                          f' - не найдены !!!')
                    continue
                print( f'\nСписок удаленных записей по условию '
                       f'{command["where"]}\n -')
                # Очищаем кеш
                cache_result.clear( ("select", command["table_name"]))
                print_list( deleted_list)

            case "help":
                print_help()

            case "exit":
                break

            case _:
                print("Команда не опознана !!!")









