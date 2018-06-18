# Программа клиента
import sys
import time
import logging
from socket import socket, AF_INET, SOCK_STREAM
from jim.utils import send_message, get_message
from errors import UsernameToLongError, ResponseCodeLenError, MandatoryKeyError, ResponseCodeError
from jim.core import JimPresence, JimMessage, Jim, JimResponse, JimGetContacts, JimAddContacts, JimDelContacts
from jim.config import *
from client_verifier import ClientVerifierBase

import logging_message.client_log_config
from logging_message.log_util import Log


# Получаем по имени клиентский логгер, он уже настроен в log_config
logger = logging.getLogger('client')
# создаем класс декоратор для логирования функций
log = Log(logger)


# Класс Клиент - класс, реализующий клиентскую часть системы.
class Client:

    def __init__(self, login):
        self.login = login

    @log
    def create_presence(self):
        """
        Сформировать ​​presence-сообщение
        :return: Словарь сообщения
        """
        # формируем сообщение
        jim_presence = JimPresence(self.login)
        message = jim_presence.to_dict()
        # возвращаем
        return message

    @log
    def translate_response(self, response):
        """
        Разбор сообщения
        :param response: Словарь ответа от сервера
        :return: корректный словарь ответа
        """
        result = Jim.from_dict(response)
        # возвращаем ответ
        return result.to_dict()

    def create_message(self, message_to, text):
        message = JimMessage(message_to, self.login, text)
        return message.to_dict()

    def read_messages(self, service):
        """
        Клиент читает входящие сообщения в бесконечном цикле
        :param client: сокет клиента
        """
        while True:
            # читаем сообщение
            #print('Читаю')
            message = get_message(service)
            #print(message)
            # там должно быть сообщение всем
            if message:
                if MESSAGE in message:
                    print("Ответ сервера MESSAGE {}".format(message[MESSAGE]))
                elif RESPONSE in message:
                    print("Ответ сервера RESPONSE {} Количество контактов {} ".format(message[RESPONSE],
                                                                                      message[QUANTITY]))
                elif ACTION in message:
                    #print("Ответ сервера ACTION {}".format(message[ACTION]))
                    print(message)


    def write_messages(self, service):
        """Клиент пишет сообщение в бесконечном цикле"""
        while True:
            # Вводим сообщение с клавиатуры
            text = input(':)>')
            # Создаем jim сообщение
            print(text)
            if text == GETCONTACTS:
                # Запрос списка контактов у сервера
                # Создаем сообщение
                get_contacts = client.create_get_contacts()
                # Отсылаем сообщение
                send_message(sock, get_contacts)
            elif text == ADDCONTACT:
                # Запрос списка контактов у сервера
                # Создаем сообщение
                add_contacts = client.create_add_contacts()
                # Отсылаем сообщение
                send_message(sock, add_contacts)
            elif text == DELCONTACT:
                # Запрос списка контактов у сервера
                # Создаем сообщение
                del_contacts = client.create_del_contacts()
                # Отсылаем сообщение
                send_message(sock, del_contacts)
            else:
                message = self.create_message('#all', text)
                #  отправляем на сервер
                send_message(service, message)

    #Создать сообщение для получения ​​списка​​ контактов
    def create_get_contacts(self):
        """
        Сформировать ​​presence-сообщение
        :return: Словарь сообщения
        """
        # формируем сообщение
        jim_get_contacts = JimGetContacts(self.login)
        message = jim_get_contacts.to_dict()
        # возвращаем
        return message

    #Создать сообщение для добавления в ​​список контактов
    def create_add_contacts(self):
        """
        Сформировать ​​presence-сообщение
        :return: Словарь сообщения
        """
        # формируем сообщение
        jim_add_contacts = JimAddContacts(self.login)
        message = jim_add_contacts.to_dict()
        # возвращаем
        return message

    #Создать сообщение для удаление из ​​списока контактов
    def create_del_contacts(self):
        """
        Сформировать ​​presence-сообщение
        :return: Словарь сообщения
        """
        # формируем сообщение
        jim_del_contacts = JimDelContacts(self.login)
        message = jim_del_contacts.to_dict()
        # возвращаем
        return message


if __name__ == '__main__':
    sock = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
    # Пытаемся получить параметры скрипта
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
    sock.connect((addr, port))
    # Создаем пользователя
    client = Client('Dmitricus')
    # Создаем сообщение
    presence = client.create_presence()
    # Отсылаем сообщение
    send_message(sock, presence)
    # Получаем ответ
    response = get_message(sock)
    # Проверяем ответ
    response = client.translate_response(response)


    if response['response'] == OK:
        # в зависимости от режима мы будем или слушать или отправлять сообщения
        if mode == 'r':
            print("Клиент запущен в режиме чтение!")
            client.read_messages(sock)
        elif mode == 'w':
            print("Клиент запущен в режиме отправки!")
            client.write_messages(sock)
        else:
            raise Exception('Не верный режим чтения/записи')


