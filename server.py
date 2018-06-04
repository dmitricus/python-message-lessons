# Программа сервера
from socket import *
import sys
import logging
import time
import select
import json
from jim.utils import bytes_to_dict, dict_to_bytes
from jim.jim_class import JIMMessage, JIMReply
from jim.config import *
from server_verifier import ServerVerifierBase

import logging_message.server_log_config
from logging_message.log_util import Log

# Получаем по имени клиентский логгер, он уже нестроен в log_config
logger = logging.getLogger('server')
# создаем класс декоратор для логирования функций
log = Log(logger)

# Класс Сервер - базовый класс сервера мессенджера; может иметь разных потомков - работающих с потоками или выполняющих асинхронную обработку.
class Server(JIMMessage, JIMReply, ServerVerifierBase):

    def __init__(self, addr='localhost', port=7777):
        self.server = socket(AF_INET, SOCK_STREAM)

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
        self.server.bind((self.addr, self.port))
        self.server.listen(100)
        self.server.settimeout(0.2)  # Таймаут для операций с сокетом


    @log
    def presence_response(self, presence_message):
        if ACTION in presence_message and \
                presence_message[ACTION] == PRESENCE and \
            TIME in presence_message and \
                isinstance(presence_message[TIME], float):
            return {RESPONSE: 200}
        else:
            return {RESPONSE: 400, ERROR: 'Не верный запрос '}


    @log
    def create_message(self, message_to, text, account_name=''):
        return {ACTION: MSG, TIME: time.time(), TO: message_to, FROM: account_name, MESSAGE: text}


    @log
    def read_requests(self, r_clients, all_clients):
        '''
        Чтение сообщений, которые будут посылать клиенты
        :param r_clients: клиенты которые могут отправлять сообщения
        :param all_clients: все клиенты
        :return:
        '''
        responses = {}      # Словарь ответов сервера вида {сокет: запрос}

        for sock in r_clients:
            try:
                data = sock.recv(1024).decode('utf-8')
                responses[sock] = data
                # Из json делаем словарь
                message = json.loads(data)
                # отправляем ответ клиенту
                if ACTION in message and message[ACTION] == MSG:
                    for sock in all_clients:
                        message[RESPONSE] = 200
                        print(message)
                        # Если там был словарь
                        if isinstance(message, dict):
                            self.send_message(sock, message)
                        else:
                            # Нам прислали неверный тип
                            raise TypeError
                print(data)
            except:
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                try:
                    all_clients.remove(sock)
                except:
                    print('Клиент отключился аварийно!')
                    logger.warning('Клиент отключился аварийно!')

        return responses


    @log
    def write_responses(self, requests, w_clients, all_clients):
        '''
        Отправка сообщений тем клиентам, которые их ждут
        :param messages: список сообщений
        :param w_clients: клиенты которые читают
        :param all_clients: все клиенты
        :return:
        '''

        for sock in w_clients:
            if sock in requests:
                try:
                    # формируем ответ
                    response = self.presence_response(bytes_to_dict(requests[sock].encode('utf-8')))
                    # отправляем ответ клиенту
                    self.send_message(sock, response)
                except:                 # Сокет недоступен, клиент отключился
                    print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                    sock.close()
                    try:
                        all_clients.remove(sock)
                    except:
                        print('Клиент отключился аварийно!')
                        logger.warning('Клиент отключился аварийно!')

    def main(self):
        '''
        Основной цикл обработки запросов клиентов
        '''
        clients = []

        while True:
            # print('В цикле')
            try:
                conn, addr = self.server.accept()  # Проверка подключений
            except OSError as e:
                pass                     # timeout вышел
            else:
                #print("Получен запрос на соединение от %s" % str(addr))
                clients.append(conn)
            finally:
                # Проверить наличие событий ввода-вывода
                wait = 0
                r = []
                w = []
                try:
                    r, w, e = select.select(clients, clients, [], wait)
                    #print('пишут:', r)
                    #print('читают:', w)
                except:
                    pass            # Ничего не делать, если какой-то клиент отключился

                #print('пишут:', r)
                requests = self.read_requests(r, clients)      # Сохраним запросы клиентов
                self.write_responses(requests, w, clients)     # Выполним отправку ответов клиентам

if __name__ == '__main__':
    print('Эхо-сервер запущен!')
    # класс создает объект (экземпляр)
    server = Server()
    server.main()
