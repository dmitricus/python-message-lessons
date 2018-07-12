# Программа клиента
import rsa
import logging
import queue
import ssl
from socket import socket, AF_INET, SOCK_STREAM
from jim.utils import send_message, get_message
from errors import UsernameToLongError, ResponseCodeLenError, MandatoryKeyError, ResponseCodeError
from jim.core import JimPresence, JimMessage, Jim, JimResponse, JimDelContact, JimAddContact, JimContactList, JimGetContacts, JimMessageCrypto
from jim.config import *
from client_verifier import ClientVerifierBase
from logging_message.log_util import Log

from auth.authenticate import client_authenticate

# Получаем по имени клиентский логгер, он уже настроен в log_config
logger = logging.getLogger('client')
# создаем класс декоратор для логирования функций
log = Log(logger)


class User:
    def __init__(self, login, password, addr, port):
        self.addr = addr
        self.port = port
        self.login = login
        self.password = password
        self.request_queue = queue.Queue()
        (self.user_pub, self.user_priv) = rsa.newkeys(512)
        self.user_public_keys = []

    def connect(self):
        # Соединиться с сервером
        try:
            #self.sock = socket(AF_INET, SOCK_STREAM)
            #self.sock = ssl.wrap_socket(socket(AF_INET, SOCK_STREAM), 'server.key', 'server.crt', True)
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock = ssl.wrap_socket(self.sock, ssl_version = ssl.PROTOCOL_SSLv3)

            self.sock.connect((self.addr, self.port))
            # Аутентификация на сервере
            client_authenticate(self.sock, secret_key)
            # Создаем сообщение
            presence = self.create_presence()
            # Отсылаем сообщение
            print(send_message(self.sock, presence))
            # Получаем ответ
            response = get_message(self.sock)
            # Проверяем ответ
            response = self.translate_response(response)
            print("Ответ сервера: ", response)
            return response
        except ConnectionRefusedError as e:
            print(e)
            raise e
        except Exception as e:
            print("Ошибка в функции connect:", e)

    def disconnect(self):
        try:
            self.sock.close()
        except Exception as e:
            print("Ошибка в функции disconnect:", e)
    @log
    def create_presence(self):
        """
        Сформировать ​​presence-сообщение
        :return: Словарь сообщения
        """
        # формируем сообщение
        jim_presence = JimPresence(self.login, self.password)
        message = jim_presence.to_dict()
        # возвращаем
        #print(message)
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
        try:
            # запрос на список контактов
            jimmessage = JimGetContacts(self.login)
            # отправляем
            send_message(self.sock, jimmessage.to_dict())
            # получаем ответ
            response = self.request_queue.get()
            quantity = response.quantity
            # получаем имена одним списком
            message = self.request_queue.get()
            # возвращаем список имен
            contacts = message.user_id
            return contacts, quantity
        except Exception as e:
            print("Ошибка в функции get_contacts:", e)

    def add_contact(self, username):
        # будем добавлять контакт
        message = JimAddContact(self.login, username)
        send_message(self.sock, message.to_dict())
        # получаем ответ от сервера
        #response = get_message(self.sock)
        #response = Jim.from_dict(response)
        response = self.request_queue.get()
        return response

    def del_contact(self, username):
        # будем удалять контакт
        message = JimDelContact(self.login, username)
        send_message(self.sock, message.to_dict())
        # получаем ответ от сервера
        #response = get_message(self.sock)
        #response = Jim.from_dict(response)
        response = self.request_queue.get()
        return response

    def send_message(self, to, text):
        message = JimMessage(to, self.login, text)
        send_message(self.sock, message.to_dict())

    def send_crypto(self, to, pub_key):
        try:
            message = JimMessageCrypto(to, self.login, pub_key)
            send_message(self.sock, message.to_dict())
            print("send_crypto: Сообщение отправлено! {}".format(message.to_dict()))
        except Exception as e:
            print("Ошибка в функции client.send_crypto:", e)

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