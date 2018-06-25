# Программа клиента
import sys
import time
import logging
from socket import socket, AF_INET, SOCK_STREAM
from jim.utils import send_message, get_message
from errors import UsernameToLongError, ResponseCodeLenError, MandatoryKeyError, ResponseCodeError
from jim.core import JimPresence, JimMessage, Jim, JimResponse, JimDelContact, JimAddContact, JimContactList, JimGetContacts
from jim.config import *
from client_verifier import ClientVerifierBase

import logging_message.client_log_config
from logging_message.log_util import Log


# Получаем по имени клиентский логгер, он уже настроен в log_config
logger = logging.getLogger('client')
# создаем класс декоратор для логирования функций
log = Log(logger)


class User:
    def __init__(self, login, addr, port):
        self.addr = addr
        self.port = port
        self.login = login

    def connect(self):
        # Соединиться с сервером
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.addr, self.port))
        # Создаем сообщение
        presence = self.create_presence()
        # Отсылаем сообщение
        send_message(self.sock, presence)
        # Получаем ответ
        response = get_message(self.sock)
        # Проверяем ответ
        response = self.translate_response(response)
        return response

    def disconnect(self):
        self.sock.close()

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

    def get_contacts(self):
        # запрос на список контактов
        jimmessage = JimGetContacts(self.login)
        # отправляем
        send_message(self.sock, jimmessage.to_dict())
        # получаем ответ
        response = get_message(self.sock)

        # приводим ответ к ответу сервера
        response = Jim.from_dict(response)
        quantity = response.quantity
        # получаем имена одним списком
        # возвращаем список имен
        contacts = []
        for i in range(quantity):
            message = get_message(self.sock)
            message = Jim.from_dict(message)
            print(message.user_id)
            contacts.append(message.user_id)
        return contacts

    def add_contact(self, username):
        # будем добавлять контакт
        message = JimAddContact(self.login, username)
        send_message(self.sock, message.to_dict())
        # получаем ответ от сервера
        response = get_message(self.sock)
        response = Jim.from_dict(response)
        return response

    def del_contact(self, username):
        # будем удалять контакт
        message = JimDelContact(self.login, username)
        send_message(self.sock, message.to_dict())
        # получаем ответ от сервера
        response = get_message(self.sock)
        response = Jim.from_dict(response)
        return response

    def send_message(self, to, text):
        message = JimMessage(to, self.login, text)
        send_message(self.sock, message.to_dict())

    def read_messages(self, service):
        """
        Клиент читает входящие сообщения в бесконечном цикле
        :param client: сокет клиента
        """
        while True:
            # читаем сообщение
            print('Читаю')
            message = get_message(service)
            print(message)
            # там должно быть сообщение всем
            print(message[MESSAGE])

    def write_messages(self, service):
        """Клиент пишет сообщение в бесконечном цикле"""
        while True:
            # Вводим сообщение с клавиатуры
            text = input(':)>')
            if text.startswith('list'):
                # запрос на список контактов
                jimmessage = JimGetContacts(self.login)
                # отправляем

                send_message(service, jimmessage.to_dict())
                # получаем ответ
                response = get_message(service)

                # приводим ответ к ответу сервера
                response = Jim.from_dict(response)
                # там лежит количество контактов
                quantity = response.quantity
                # делаем цикл и получаем каждый контакт по отдельности
                print('У вас ', quantity, 'друзей')
                print('Вот они:')
                for i in range(quantity):
                    message = get_message(service)
                    message = Jim.from_dict(message)
                    print(message.user_id)
            else:
                command, param = text.split()
                if command == 'add':
                    # будем добавлять контакт
                    message = JimAddContact(self.login, param)
                    send_message(service, message.to_dict())
                    # получаем ответ от сервера
                    response = get_message(service)
                    response = Jim.from_dict(response)
                    if response.response == ACCEPTED:
                        print('Контакт успешно добавлен')
                    else:
                        print(response.error)
                elif command == 'del':
                    # будем удалять контакт
                    message = JimDelContact(self.login, param)
                    send_message(service, message.to_dict())
                    # получаем ответ от сервера
                    response = get_message(service)
                    response = Jim.from_dict(response)
                    if response.response == ACCEPTED:
                        print('Контакт успешно удален')
                    else:
                        print(response.error)

            # # Создаем jim сообщение
            # message = self.create_message('#all', text)
            # # отправляем на сервер
            # send_message(service, message)


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
        mode = 'w'
    # Соединиться с сервером
    sock.connect((addr, port))
    # Создаем пользователя
    user = User('Dmitricus')
    # Создаем сообщение
    presence = user.create_presence()
    # Отсылаем сообщение
    send_message(sock, presence)
    # Получаем ответ
    response = get_message(sock)
    # Проверяем ответ
    response = user.translate_response(response)
    if response['response'] == OK:
        # в зависимости от режима мы будем или слушать или отправлять сообщения
        if mode == 'r':
            user.read_messages(sock)
        elif mode == 'w':
            user.write_messages(sock)
        else:
            raise Exception('Не верный режим чтения/записи')
