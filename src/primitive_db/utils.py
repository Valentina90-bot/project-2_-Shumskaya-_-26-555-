import json
import os

from primitive_db.constants import META_FILE


def load_metadata(filepath=META_FILE):
    """Загружает метаданные таблиц базы данных из JSON-файла."""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_metadata(data, filepath=META_FILE):
    """Сохраняет измененные метаданные таблиц базы данных в JSON-файл."""
    if isinstance(data, str) and isinstance(filepath, dict):
        data, filepath = filepath, data

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_table_data(table_name):
    """Загружает массив записей конкретной таблицы из соответствующего JSON-файла."""
    file_path = os.path.join("data", f"{table_name}.json")
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_table_data(table_name, data):
    """Сохраняет массив записей таблицы на диск в файл формата JSON."""
    os.makedirs("data", exist_ok=True)
    file_path = os.path.join("data", f"{table_name}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
