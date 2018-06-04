# Программа клиента
import sys
import time
import logging
from socket import *
from errors import UsernameToLongError, ResponseCodeLenError, MandatoryKeyError, ResponseCodeError
from jim.jim_class import JIMMessage, JIMReply
from jim.config import *
from client_verifier import ClientVerifierBase

import logging_message.client_log_config
from logging_message.log_util import Log


# Получаем по имени клиентский логгер, он уже нестроен в log_config
logger = logging.getLogger('client')
# создаем класс декоратор для логирования функций
log = Log(logger)


# Класс Клиент - класс, реализующий клиентскую часть системы.
class Client(JIMMessage, JIMReply, ClientVerifierBase):

    def __init__(self, addr='localhost', port=7777, mode='r'):
        self.client = socket(AF_INET, SOCK_STREAM)

        try:
            self.addr = sys.argv[1]
        except IndexError:
            self.addr = addr
        try:
            self.port = int(sys.argv[2])
        except IndexError:
            self.port = port
        except ValueError:
            print('Порт должен быть целым числом')
            sys.exit(0)
        try:
            self.mode = sys.argv[3]
        except IndexError:
            self.mode = mode

        # Соединиться с сервером
        self.client.connect((self.addr, self.port))

    @log
    def create_presence(self, account_name='Guest'):
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

    @log
    def translate_response(self, response):
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

    @log
    def create_message(self, message_to, text, account_name='Guest'):
        return {ACTION: MSG, TIME: time.time(), TO: message_to, FROM: account_name, MESSAGE: text}


    @log
    def read_messages(self):

        while True:
            # читаем сообщение
            #print('Читаю')
            message = self.get_message(self.client)
            if MESSAGE in message:
                # там должно быть сообщение всем
                print('{}: {}'.format(message[FROM], message[MESSAGE]))
            else:
                print(message)


    @log
    def write_messages(self):
        while True:
            # Вводим сообщение с клавиатуры
            text = input(':)>')
            # Создаем jim сообщение
            message = self.create_message('#all', text)
            # отправляем на сервер
            self.send_message(self.client, message)

    def main(self):
        # Создаем сообщение
        presence = self.create_presence()
        # Отсылаем сообщение
        self.send_message(self.client, presence)
        # Получаем ответ
        response = self.get_message(self.client)
        print(response)
        # Проверяем ответ
        response = self.translate_response(response)

        if response['response'] == OK:
            # в зависимости от режима мы будем или слушать или отправлять сообщения
            if self.mode == 'r':
                self.read_messages()
            elif self.mode == 'w':
                self.write_messages()
            else:
                raise Exception('Не верный режим чтения/записи')

if __name__ == '__main__':
    print('Клиент запущен!')
    # класс создает объект (экземпляр)
    client = Client()
    client.main()
