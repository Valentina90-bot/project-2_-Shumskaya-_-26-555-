from prettytable import PrettyTable

from primitive_db.core import create_table, delete, drop_table, insert, select, update
from primitive_db.decorators import create_cacher
from primitive_db.parser import parse_insert_values, parse_set, parse_where
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def show_help():
    print("\n***Операции с данными***\n")
    print("Функции:")
    print(
        "insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись."
    )
    print(
        "select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию."
    )
    print("select from <имя_таблицы> - прочитать все записи.")
    print(
        "update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print("delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.")
    print("info <имя_таблицы> - вывести информацию о таблице.")
    print("exit - выход из программы")
    print("help - справочная информация\n")


def main():
    metadata = load_metadata("db_meta.json")
    cache_result = create_cacher()
    show_help()

    while True:
        try:
            user_input = input(">>> Введите команду: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        cmd_lower = user_input.lower()

        if cmd_lower == "exit":
            break
        elif cmd_lower == "help":
            show_help()
            continue

        if cmd_lower.startswith("create_table "):
            parts = user_input.split()
            if len(parts) < 3:
                print("Ошибка: Неверный формат команды create_table.")
                continue
            table_name = parts[1]
            columns_raw = parts[2:]
            columns = {}
            for col in columns_raw:
                if ":" not in col:
                    continue
                c_name, c_type = col.split(":", 1)
                columns[c_name] = c_type
            try:
                metadata = create_table(metadata, table_name, columns)
                save_metadata(metadata, "db_meta.json")
                print(f'Таблица "{table_name}" успешно создана.')
            except ValueError as e:
                print(e)
            continue

        elif cmd_lower.startswith("drop_table "):
            parts = user_input.split()
            if len(parts) < 2:
                print("Ошибка: Укажите имя таблицы.")
                continue
            table_name = parts[1]
            try:
                metadata = drop_table(metadata, table_name)
                save_metadata(metadata, "db_meta.json")
                print(f'Таблица "{table_name}" успешно удалена.')
            except ValueError as e:
                print(e)
            continue

        elif cmd_lower.startswith("list_tables"):
            if not metadata:
                print("Нет созданных таблиц.")
            else:
                for t_name in metadata:
                    print(f"- {t_name}")
            continue

        elif cmd_lower.startswith("insert into "):
            parts = user_input.split(maxsplit=2)
            if len(parts) < 3:
                print("Ошибка: Неверный формат команды insert.")
                continue

            table_name = parts[2].split()[0]
            values_idx = user_input.lower().find("values")
            values_str = user_input[values_idx:] if values_idx != -1 else ""
            values = parse_insert_values(values_str)

            try:
                table_data = load_table_data(table_name)

                current_schema = metadata.get(table_name, {})
                if isinstance(current_schema, dict):
                    schema_list = list(current_schema.keys())
                else:
                    schema_list = list(current_schema)

                temp_metadata = {table_name: schema_list}

                table_data = insert(temp_metadata, table_name, values, table_data)
                save_table_data(table_name, table_data)
                new_id = table_data[-1]["ID"] if table_data else 1
                print(
                    f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".'
                )
            except (ValueError, TypeError) as e:
                print(e)
            continue

        elif cmd_lower.startswith("select from "):
            parts = user_input.split()
            if len(parts) < 3:
                print("Ошибка: Укажите таблицу.")
                continue
            table_name = parts[2]
            where_clause = None
            if "where" in cmd_lower:
                where_str = user_input[user_input.lower().find("where") :]
                where_clause = parse_where(where_str)

            if table_name not in metadata:
                print(f"Ошибка: Таблица '{table_name}' не существует.")
                continue

            cache_key = f"{table_name}_{str(where_clause)}"

            def get_data():
                table_data = load_table_data(table_name)
                return select(table_data, where_clause)

            results = cache_result(cache_key, get_data)

            if not results:
                print("Записи не найдены.")
                continue

            schema = metadata[table_name]
            pt = PrettyTable()

            if isinstance(schema, dict):
                fields = list(schema.keys())
            else:
                fields = [col for col in schema if col != "ID"]

            pt.field_names = ["ID"] + fields
            for row in results:
                row_vals = [row.get("ID")] + [row.get(col) for col in fields]
                pt.add_row(row_vals)
            print(pt)
            continue

        elif cmd_lower.startswith("update "):
            parts = user_input.split()
            if len(parts) < 2:
                print("Ошибка: Укажите таблицу.")
                continue
            table_name = parts[1]
            if "set" not in cmd_lower:
                print("Ошибка: Отсутствует ключевое слово set.")
                continue
            set_str = user_input[user_input.lower().find("set") :]
            set_clause, where_clause = parse_set(set_str)
            if not where_clause:
                print("Ошибка: Команда update требует условие where.")
                continue

            table_data = load_table_data(table_name)
            table_data = update(table_data, set_clause, where_clause)
            save_table_data(table_name, table_data)
            print(f'Записи в таблице "{table_name}" успешно обновлены.')
            continue

        elif cmd_lower.startswith("delete from "):
            parts = user_input.split()
            if len(parts) < 3:
                print("Ошибка: Укажите таблицу.")
                continue
            table_name = parts[2]
            if "where" not in cmd_lower:
                print("Ошибка: Команда delete требует условие where.")
                continue
            where_str = user_input[user_input.lower().find("where") :]
            where_clause = parse_where(where_str)

            table_data = load_table_data(table_name)
            table_data = delete(table_data, where_clause)
            save_table_data(table_name, table_data)
            print(f'Записи успешно удалены из таблицы "{table_name}".')
            continue

        elif cmd_lower.startswith("info "):
            parts = user_input.split()
            table_name = parts[1]
            if table_name not in metadata:
                print(f"Ошибка: Таблица '{table_name}' не существует.")
                continue
            schema = metadata[table_name]
            table_data = load_table_data(table_name)

            if isinstance(schema, dict):
                cols_str = ", ".join([f"{k}:{v}" for k, v in schema.items()])
            else:
                cols_str = ", ".join([f"{col}:str" for col in schema if col != "ID"])

            print(f"Таблица: {table_name}")
            print(f"Столбцы: ID:int, {cols_str}")
            print(f"Количество записей: {len(table_data)}")
            continue

        else:
            print("Ошибка: Неизвестная команда.")


if __name__ == "__main__":
    main()
