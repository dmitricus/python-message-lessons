# Программа клиента
import sys
import time
from socket import *
from jim.utils import encode, decode
from jim.config import *

account_name = "User"

message = {
    ACTION: PRESENCE,
    TIME: time.time(),
    USER: {
        ACCOUNT_NAME: account_name
    }
}

if __name__ == '__main__':
    s = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP
    # Получаем аргументы скрипта
    try:
         addr = sys.argv[1]
    except IndexError:
         addr = 'localhost'
    try:
        port = int(sys.argv[2])
    except IndexError:
        port = 7777
    except ValueError:
        print('Порт должен быть целым числом')
        sys.exit(0)

    s.connect((addr, port))                 # Соединиться с сервером
    s.send(encode(message))                 # Отправить запрос серверу
    print("Отправлено сообщение серверу")
    data = s.recv(1024)                     # Принять не более 1024 байтов данных
    s.close()


    print("Получен ответ от сервера:", data)