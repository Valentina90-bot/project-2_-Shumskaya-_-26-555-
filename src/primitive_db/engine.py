import prompt

def welcome():
    print("\nПервая попытка запустить проект!\n")
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    
    # Запрашиваем ввод у пользователя с помощью библиотеки prompt
    command = prompt.string("Введите команду: ")
    
    # Если пользователь ввел help, выводим справочную информацию
    if command == "help":
        print("\n<command> exit - выйти из программы")
        print("<command> help - справочная информация")
        prompt.string("Введите команду: ")
