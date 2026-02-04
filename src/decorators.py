import time
from functools import wraps


def handle_db_errors(func):
    """Обработка ошибок"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден !!!")
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
    return wrapper


def confirm_action(action_name: str):
    """
    Декоратор-фабрика:
    По умолчанию спрашивает подтверждение через input().
    Если в аргументах функции есть yes=True (или y=True) — подтверждение пропускается.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Автоподтверждение (например, для тестов или режима --yes)
            if kwargs.pop("yes", False) or kwargs.pop("y", False):
                return func(*args, **kwargs)

            answer = input(f"Подтвердите {action_name}? (y/n): ").strip().lower()

            if answer in ("y", "yes", "д", "да"):
                return func(*args, **kwargs)

            print("Операция отменена.")
            return None

        return wrapper

    return decorator


def log_time(func):
    """
    Декоратор для замера времени выполнения функции.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            end = time.monotonic()
            duration = end - start
            print(f"[TIME] {func.__name__} выполнена за {duration:.6f} сек")

    return wrapper



