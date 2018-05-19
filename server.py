# Программа сервера
from socket import *
import sys
from jim.utils import encode, decode
from jim.config import *


def presence_response(presence_message):
    if ACTION in presence_message and \
        presence_message[ACTION] == PRESENCE and \
        TIME in presence_message and \
            isinstance(presence_message[TIME], float):
        return {RESPONSE: 200}
    else:
        return {RESPONSE: 400, ERROR: 'Не верный запрос '}

if __name__ == '__main__':
    server = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP
    # Получаем аргументы скрипта
    try:
         addr = sys.argv[1]
    except IndexError:
         addr = ''
    try:
        port = int(sys.argv[2])
    except IndexError:
        port = 7777
    except ValueError:
        print('Порт должен быть целым числом')
        sys.exit(0)

    server.bind((addr, port))                                       # присваеиваем порт 7777
    server.listen(5)

    while True:
        client, addr = server.accept()                              # Принять запрос на соединение
        #print(type(client))
        print("Получен запрос на соединение от %s" % str(addr))


        data = client.recv(1024)                                    # Получаем запрос от клиента
        print("Получен запрос от клиента:", decode(data))

        # Подготовим ответ клиенту
        presence = encode(presence_response(decode(data)))                  # переводим словарь в байты
        client.send(presence)                                       # Отправляем сообщение слиенту
        print("Отправлено сообщение клиенту", presence)

        # Закрываем соединение с клиентом
        client.close()