# Программа сервера
from socket import *
import sys
import logging
import time
import select
from socket import socket, AF_INET, SOCK_STREAM
from jim.utils import send_message, get_message
from jim.core import Jim, JimMessage, JimResponse, JimResponseGetContacts, JimContactsList, JimResponseAddContacts, JimResponseDelContacts
from jim.config import *
from db.controller import Storage
from db.models import User, CustomerHistory, ContactList

from server_verifier import ServerVerifierBase

import logging_message.server_log_config
from logging_message.log_util import Log

# Получаем по имени клиентский логгер, он уже нестроен в log_config
logger = logging.getLogger('server')
# создаем класс декоратор для логирования функций
log = Log(logger)

class Handler:
    """Обработчик сообщений, тут будет основная логика сервера"""

    def read_requests(self, r_clients, all_clients):
        """
        Чтение сообщений, которые будут посылать клиенты
        :param r_clients: клиенты которые могут отправлять сообщения
        :param all_clients: все клиенты
        :return:
        """
        # Список входящих сообщений
        messages = []

        for sock in r_clients:
            try:
                # Получаем входящие сообщения
                message = get_message(sock)
                # Добавляем их в список
                # В идеале нам нужно сделать еще проверку, что сообщение нужного формата прежде чем его пересылать!
                # Пока оставим как есть, этим займемся позже
                messages.append(message)
            except:
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                all_clients.remove(sock)

        # Возвращаем словарь сообщений
        return messages


    def write_responses(self, messages, w_clients, all_clients):
        """
        Отправка сообщений тем клиентам, которые их ждут
        :param messages: список сообщений
        :param w_clients: клиенты которые читают
        :param all_clients: все клиенты
        :return:
        """

        # Будем отправлять каждое сообщение всем
        for sock in w_clients:
            for message in messages:
                try:
                    if ACTION in message:
                        if message[ACTION] == GETCONTACTS:
                            # формируем ответ о списке контактов
                            response, contact_list = self.get_contacts_response(message)
                            # отправляем ответ клиенту
                            send_message(sock, response)
                            # задержка
                            time.sleep(0.1)
                            for contact_response in contact_list:
                                send_message(sock, contact_response)
                                # задержка
                                time.sleep(0.1)
                        elif message[ACTION] == ADDCONTACT:
                            response = self.add_contact_response(message)
                            # отправляем ответ клиенту
                            send_message(sock, response)
                        elif message[ACTION] == DELCONTACT:
                            response = self.del_contact_response(message)
                            # отправляем ответ клиенту
                            send_message(sock, response)
                        elif message[ACTION] == PRESENCE:
                            # Отправить на тот сокет, который ожидает отправки
                            send_message(sock, message)
                except:  # Сокет недоступен, клиент отключился
                    print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                    sock.close()
                    all_clients.remove(sock)


    def presence_response(self, presence_message):
        """
        Формирование ответа клиенту
        :param presence_message: Словарь presence запроса
        :return: Словарь ответа
        """
        # Делаем проверки
        try:
            Jim.from_dict(presence_message)
        except Exception as e:
            # Шлем код ошибки
            response = JimResponse(400, error=str(e))
            return response.to_dict()
        else:
            # Если всё хорошо шлем ОК
            response = JimResponse(200)
            return response.to_dict()


    def get_contacts_response(self, get_contacts_message):
        """
        Формирование ответа клиенту
        :param presence_message: Словарь presence запроса
        :return: Словарь ответа
        """
        # Делаем проверки
        try:
            Jim.from_dict(get_contacts_message)
        except Exception as e:
            # Шлем код ошибки
            response = JimResponseGetContacts(400, error=str(e))
            return response.to_dict()
        else:
            q_contact_list, quantity = storage.select_contact_list(get_contacts_message[ACCOUNT_NAME])
            # Если всё хорошо шлем ОК
            response = JimResponseGetContacts(202, quantity=quantity)
            contact_list = []
            for user_id in q_contact_list:
                response_contact = JimContactsList(user_id[0])
                contact_list.append(response_contact.to_dict())
            return response.to_dict(), contact_list


    def add_contact_response(self, add_contacts_message):
        """
        Формирование ответа клиенту
        :param presence_message: Словарь presence запроса
        :return: Словарь ответа
        """
        # Делаем проверки
        try:
            Jim.from_dict(add_contacts_message)
        except Exception as e:
            # Шлем код ошибки
            response = JimResponseAddContacts(400, error=str(e))
            return response.to_dict()
        else:
            storage.insert_contact_list(add_contacts_message[ACCOUNT_NAME])
            # Если всё хорошо шлем ОК
            response = JimResponseAddContacts(202)
            return response.to_dict()

    def del_contact_response(self, del_contacts_message):
        """
        Формирование ответа клиенту
        :param presence_message: Словарь presence запроса
        :return: Словарь ответа
        """
        # Делаем проверки
        try:
            Jim.from_dict(del_contacts_message)
        except Exception as e:
            # Шлем код ошибки
            response = JimResponseDelContacts(400, error=str(e))
            return response.to_dict()
        else:
            storage.insert_contact_list(del_contacts_message[ACCOUNT_NAME])
            # Если всё хорошо шлем ОК
            response = JimResponseDelContacts(202)
            return response.to_dict()

# Класс Сервер - базовый класс сервера мессенджера; может иметь разных потомков - работающих с потоками или выполняющих асинхронную обработку.
class Server:

    def __init__(self, handler):
        """
            :param handler: обработчик событий
        """
        self.handler = handler
        # список клиентов
        self.clients = []
        # сокет
        self.sock = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP

    def bind(self, addr, port):
        # запоминаем адрес и порт
        self.sock.bind((addr, port))

    def listen_forever(self):
        # запускаем цикл обработки событиц много клиентов
        self.sock.listen(15)
        self.sock.settimeout(0.2)

        while True:
            try:
                conn, addr = self.sock.accept()  # Проверка подключений
                # получаем сообщение от клиента
                presence = get_message(conn)
                # формируем ответ
                response = self.handler.presence_response(presence)
                # отправляем ответ клиенту
                send_message(conn, response)
            except OSError as e:
                pass  # timeout вышел
            else:
                print("Получен запрос на соединение от %s" % str(addr))
                # Добавляем клиента в список
                self.clients.append(conn)
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
                self.handler.write_responses(requests, w, self.clients)  # Выполним отправку входящих сообщений

if __name__ == '__main__':
    user = User
    customer_history = CustomerHistory
    contact_list = ContactList
    storage = Storage(user, customer_history, contact_list)


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
    print("Сервер запущен!")
    handler = Handler()
    server = Server(handler)
    server.bind(addr, port)
    server.listen_forever()
