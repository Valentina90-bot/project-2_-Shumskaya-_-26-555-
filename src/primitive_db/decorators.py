import time
from functools import wraps


def handle_db_errors(func):
    """Декоратор для централизованной обработки исключений СУБД."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except TypeError as e:
            print(f"Ошибка типов: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

    return wrapper


def confirm_action(action_name):
    """Декоратор для подтверждения опасных операций пользователем."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = (
                input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
                .strip()
                .lower()
            )
            if response == "y":
                return func(*args, **kwargs)
            else:
                print("Операция отменена.")

        return wrapper

    return decorator


def log_time(func):
    """Декоратор для замера и вывода времени выполнения функции."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        execution_time = end_time - start_time
        print(f"Функция <{func.__name__}> выполнилась за {execution_time:.3f} секунд.")
        return result

    return wrapper


def create_cacher():
    """Создает и возвращает внутреннюю функцию для кэширования запросов."""
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    return cache_result
