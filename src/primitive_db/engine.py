import shlex
import prompt
from primitive_db.utils import load_metadata, save_metadata
from primitive_db.core import create_table, drop_table

DB_FILE = "db_meta.json"

def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def run():
    print_help()
    while True:
        metadata = load_metadata(DB_FILE)
        user_input = prompt.string("Введите команду: ")
        
        if not user_input:
            continue
            
        args = shlex.split(user_input)
        command = args[0]
        
        if command == "exit":
            break
        elif command == "help":
            print_help()
        elif command == "list_tables":
            if not metadata:
                print("Нет созданных таблиц.")
            for table_name in metadata:
                print(f"- {table_name}")
        elif command == "create_table":
            if len(args) < 2:
                print("Некорректное значение: пропущено имя таблицы. Попробуйте снова.")
                continue
            table_name = args[1]
            columns = args[2:]
            new_metadata = create_table(metadata, table_name, columns)
            if new_metadata != metadata or table_name in new_metadata:
                save_metadata(DB_FILE, new_metadata)
        elif command == "drop_table":
            if len(args) < 2:
                print("Некорректное значение: пропущено имя таблицы. Попробуйте снова.")
                continue
            table_name = args[1]
            new_metadata = drop_table(metadata, table_name)
            save_metadata(DB_FILE, new_metadata)
        else:
            print(f"Функции {command} нет. Попробуйте снова.")
