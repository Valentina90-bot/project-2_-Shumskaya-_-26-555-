from primitive_db.decorators import confirm_action, handle_db_errors, log_time


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создает новую таблицу в метаданных базы данных, если она не существует."""
    if table_name in metadata:
        raise ValueError(f"Ошибка: Таблица '{table_name}' уже существует.")
    metadata[table_name] = columns
    return metadata


@confirm_action("удаление таблицы")
@handle_db_errors
def drop_table(metadata, table_name):
    """Удалет таблицу из метаданых базы данных по ее имени."""
    if table_name not in metadata:
        raise ValueError(f"Ошибка: Таблица '{table_name}' не существует.")
    del metadata[table_name]
    return metadata


@log_time
@handle_db_errors
def insert(metadata, table_name, values, table_data):
    """Проверяет типы и добавляет новую запись в массив данных таблицы."""
    if table_name not in metadata:
        raise ValueError(f"Ошибка: Таблица '{table_name}' не существует.")

    schema = metadata[table_name]
    cols_with_types = {}
    if isinstance(schema, dict):
        cols_with_types = {k: v for k, v in schema.items() if k != "ID"}
    else:
        for col in schema:
            if col != "ID":
                if col == "name":
                    cols_with_types[col] = "str"
                elif col == "age":
                    cols_with_types[col] = "int"
                elif col == "is_active":
                    cols_with_types[col] = "bool"
                else:
                    cols_with_types[col] = "str"

    col_names = list(cols_with_types.keys())
    if len(values) != len(col_names):
        raise ValueError(
            f"Ошибка: Ожидалось {len(col_names)} значений, получено {len(values)}."
        )

    validated_row = {}
    for i in range(len(values)):
        col_name = col_names[i]
        col_type = cols_with_types[col_name]
        val = values[i]

        if col_type == "int":
            if not isinstance(val, int) or isinstance(val, bool):
                raise TypeError(f"Ошибка: Столбец '{col_name}' должен быть типом int.")
        elif col_type == "bool":
            if not isinstance(val, bool):
                raise TypeError(f"Ошибка: Столбец '{col_name}' должен быть типом bool.")
        elif col_type == "str":
            if not isinstance(val, str):
                raise TypeError(f"Ошибка: Столбец '{col_name}' должен быть типом str.")
        validated_row[col_name] = val

    next_id = max([row["ID"] for row in table_data]) + 1 if table_data else 1
    new_row = {"ID": next_id}
    new_row.update(validated_row)
    table_data.append(new_row)
    return table_data


@log_time
@handle_db_errors
def select(table_data, where_clause=None):
    """Фильтрует и возвращает записи из таблицы по заданному условию."""
    if not where_clause:
        return table_data

    filtered_data = []
    for row in table_data:
        match = True
        for col_name, target_val in where_clause.items():
            if col_name not in row or row[col_name] != target_val:
                match = False
                break
        if match:
            filtered_data.append(row)
    return filtered_data


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет значения столбцов в записях таблицы по заданному условию."""
    for row in table_data:
        match = True
        for col_name, target_val in where_clause.items():
            if col_name not in row or row[col_name] != target_val:
                match = False
                break
        if match:
            for set_col, set_val in set_clause.items():
                if set_col in row and set_col != "ID":
                    row[set_col] = set_val
    return table_data


@confirm_action("удаление записей")
@handle_db_errors
def delete(table_data, where_clause):
    """Принудительно удаляет записи из таблицы, соответствующие условию фильтра."""
    table_data[:] = [
        row
        for row in table_data
        if not all(col in row and row[col] == val for col, val in where_clause.items())
    ]
    return table_data
