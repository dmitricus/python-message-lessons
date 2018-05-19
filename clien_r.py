# Программа клиента
import sys
import time
from socket import *
from errors import UsernameToLongError, ResponseCodeLenError, MandatoryKeyError, ResponseCodeError
from jim.utils import get_message, send_message, bytes_to_dict, dict_to_bytes
from jim.config import *


def create_presence(account_name='Guest'):
    if not isinstance(account_name, str):
        raise TypeError
    if len(account_name) > 25:
        raise UsernameToLongError(account_name)
    message = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    return message

def translate_response(response):
    # Передали не словарь
    if not isinstance(response, dict):
        raise TypeError
    # Нету ключа response
    if RESPONSE not in response:
        # Ошибка нужен обязательный ключ
        raise MandatoryKeyError(RESPONSE)
    # получаем код ответа
    code = response[RESPONSE]
    # длина кода не 3 символа
    if len(str(code)) != 3:
        # Ошибка неверная длина кода ошибки
        raise ResponseCodeLenError(code)
    # неправильные коды символов
    if code not in RESPONSE_CODES:
        # ошибка неверный код ответа
        raise ResponseCodeError(code)
    # возвращаем ответ
    return response

def create_message(message_to, text, account_name='Guest'):
    return {ACTION: MSG, TIME: time.time(), TO: message_to, FROM: account_name, MESSAGE: text}

def read_messages(client):

    while True:
        # читаем сообщение
        #print('Читаю')
        message = get_message(client)
        if MESSAGE in message:
            # там должно быть сообщение всем
            print('{}: {}'.format(message[FROM], message[MESSAGE]))
        else:
            print(message)

def write_messages(client):
    while True:
        # Вводим сообщение с клавиатуры
        text = input(':)>')
        # Создаем jim сообщение
        message = create_message('#all', text)
        # отправляем на сервер
        send_message(client, message)


if __name__ == '__main__':
    client = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP
    mode = 'r'
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
    try:
        mode = sys.argv[3]
    except IndexError:
        mode = 'r'

    # Соединиться с сервером
    client.connect((addr, port))
    # Создаем сообщение
    presence = create_presence()
    # Отсылаем сообщение
    send_message(client, presence)
    # Получаем ответ
    response = get_message(client)
    print(response)
    # Проверяем ответ
    response = translate_response(response)

    if response['response'] == OK:
        # в зависимости от режима мы будем или слушать или отправлять сообщения
        if mode == 'r':
            read_messages(client)
        elif mode == 'w':
            write_messages(client)
        else:
            raise Exception('Не верный режим чтения/записи')
