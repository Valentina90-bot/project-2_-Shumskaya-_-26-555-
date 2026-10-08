def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    valid_types = {"int", "str", "bool"}
    parsed_columns = [("ID", "int")]
    
    for col in columns:
        if ":" not in col:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata
        name, col_type = col.split(":", 1)
        if col_type not in valid_types:
            print(f"Некорректное значение: {col_type}. Попробуйте снова.")
            return metadata
        parsed_columns.append((name, col_type))

    metadata[table_name] = parsed_columns
    
    cols_str = ", ".join([f"{name}:{col_type}" for name, col_type in parsed_columns])
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')
    return metadata

def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata
