# Программа сервера
from socket import *
import sys
import logging
import time
import select
from queue import Queue
from threading import Thread
from multiprocessing import Process
from socket import socket, AF_INET, SOCK_STREAM
from jim.utils import send_message, get_message
from jim.core import Jim, JimMessage, JimResponse, JimContactList, JimAddContact, JimDelContact
from jim.exceptions import WrongInputError
from jim.config import *
from db.server_models import session
from db.server_controller import Storage
from db.server_errors import ContactDoesNotExist


from server_verifier import ServerVerifierBase

import logging_message.server_log_config
from logging_message.log_util import Log

# Получаем по имени клиентский логгер, он уже нестроен в log_config
logger = logging.getLogger('server')
# создаем класс декоратор для логирования функций
log = Log(logger)

class Handler:
    """Обработчик сообщений, тут будет основная логика сервера"""
    def __init__(self):
        # сохраняем репозиторий
        self.storage = Storage(session)

    def read_requests(self, names, all_clients):
        """
        Чтение сообщений, которые будут посылать клиенты
        :param r_clients: клиенты которые могут отправлять сообщения
        :param all_clients: все клиенты
        :return:
        """
        # Список входящих сообщений
        messages = []

        for sock in names:
            try:
                # Получаем входящие сообщения

                message = get_message(sock)
                # Добавляем их в список
                # В идеале нам нужно сделать еще проверку, что сообщение нужного формата прежде чем его пересылать!
                # Пока оставим как есть, этим займемся позже
                messages.append((message, sock))
            except:
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                all_clients.remove(sock)

        # Возвращаем словарь сообщений
        return messages


    def write_responses(self, messages, names, all_clients):
        """
        Отправка сообщений тем клиентам, которые их ждут
        :param messages: список сообщений
        :param w_clients: клиенты которые читают
        :param all_clients: все клиенты
        :return:
        """

        # Будем отправлять каждое сообщение всем
        for message, sock in messages:
            try:
                # теперь нам приходят разные сообщения, будем их обрабатывать
                action = Jim.from_dict(message)
                if action.action == GET_CONTACTS:
                    # нам нужен репозиторий
                    contacts = self.storage.get_contacts(action.account_name)
                    # формируем ответ
                    response = JimResponse(ACCEPTED, quantity=len(contacts))
                    # Отправляем
                    send_message(sock, response.to_dict())
                    # в цикле по контактам шлем сообщения
                    #for contact in contacts:
                    #    message = JimContactList(contact.Name)
                    #    print(message.to_dict())
                    #    send_message(sock, message.to_dict())
                    contact_names = [contact.Name for contact in contacts]
                    message = JimContactList(contact_names)
                    send_message(sock, message.to_dict())
                elif action.action == ADD_CONTACT:
                    user_id = action.user_id
                    username = action.account_name
                    try:
                        self.storage.add_contact(username, user_id)
                        # шлем удачный ответ
                        response = JimResponse(ACCEPTED)
                        # Отправляем
                        send_message(sock, response.to_dict())
                    except ContactDoesNotExist as e:
                        # формируем ошибку, такого контакта нет
                        response = JimResponse(WRONG_REQUEST, error='Такого контакта нет')
                        # Отправляем
                        send_message(sock, response.to_dict())
                elif action.action == DEL_CONTACT:
                    user_id = action.user_id
                    username = action.account_name
                    try:
                        self.storage.del_contact(username, user_id)
                        # шлем удачный ответ
                        response = JimResponse(ACCEPTED)
                        # Отправляем
                        send_message(sock, response.to_dict())
                    except ContactDoesNotExist as e:
                        # формируем ошибку, такого контакта нет
                        response = JimResponse(WRONG_REQUEST, error='Такого контакта нет')
                        # Отправляем
                        send_message(sock, response.to_dict())
                elif action.action == MSG:
                    to = action.to
                    client_sock = names[to]
                    send_message(client_sock, action.to_dict())
            except WrongInputError as e:
                # Отправляем ошибку и текст из ошибки
                response = JimResponse(WRONG_REQUEST, error=str(e))
                send_message(sock, response.to_dict())
            except:  # Сокет недоступен, клиент отключился
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                sock.close()
                all_clients.remove(sock)

    @log
    def presence_response(self, presence_message):
        """
        Формирование ответа клиенту
        :param presence_message: Словарь presence запроса
        :return: Словарь ответа
        """
        # Делаем проверки
        try:
            presence = Jim.from_dict(presence_message)
            username = presence.account_name
            # сохраняем пользователя в базу если его там еще нет
            if not self.storage.client_exists(username):
                self.storage.add_client(username)
        except Exception as e:
            # Шлем код ошибки
            response = JimResponse(WRONG_REQUEST, error=str(e))
            return response.to_dict(), None
        else:
            # Если всё хорошо шлем ОК
            response = JimResponse(OK)
            return response.to_dict(), username


class Server:
    """Клесс сервер"""

    def __init__(self, handler):
        """
        :param handler: обработчик событий
        """
        self.handler = handler
        # список клиентов
        self.clients = []
        self.names = {}
        # сокет
        self.sock = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP

    def bind(self, addr, port):
        # запоминаем адрес и порт
        self.sock.bind((addr, port))

    def listen_forever(self):
        # запускаем цикл обработки событиц много клиентов
        self.sock.listen(15)
        self.sock.settimeout(0.2)
        print('Сервер запущен')

        while True:
            try:
                conn, addr = self.sock.accept()  # Проверка подключений
                # получаем сообщение от клиента
                presence = get_message(conn)
                # формируем ответ
                response, client_name = self.handler.presence_response(presence)
                # отправляем ответ клиенту
                send_message(conn, response)
            except OSError as e:
                pass  # timeout вышел
            else:
                print("Получен запрос на соединение от %s" % str(addr))
                # Добавляем клиента в список
                self.clients.append(conn)
                self.names[client_name] = conn
                print('Подключился {}'.format(client_name))
            finally:
                # Проверить наличие событий ввода-вывода
                wait = 0
                r = []
                w = []
                try:
                    r, w, e = select.select(self.clients, self.clients, [], wait)
                except:
                    pass  # Ничего не делать, если какой-то клиент отключился
                requests = self.handler.read_requests(r, self.clients)  # Получаем входные сообщения
                self.handler.write_responses(requests, self.names, self.clients)  # Выполним отправку входящих сообщений




if __name__ == '__main__':
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

    handler = Handler()
    server = Server(handler)
    server.bind(addr, port)
    server.listen_forever()
