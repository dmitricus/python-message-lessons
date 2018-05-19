# Программа сервера
from socket import *
import sys
import time
import select
import json
from jim.utils import get_message, send_message, bytes_to_dict, dict_to_bytes
from jim.config import *
from logging_message.log_util import *

@Log(show_params=False)
def presence_response(presence_message):
    if ACTION in presence_message and \
        presence_message[ACTION] == PRESENCE and \
        TIME in presence_message and \
            isinstance(presence_message[TIME], float):
        return {RESPONSE: 200}
    else:
        return {RESPONSE: 400, ERROR: 'Не верный запрос '}


@Log(show_params=False)
def create_message(message_to, text, account_name=''):
    return {ACTION: MSG, TIME: time.time(), TO: message_to, FROM: account_name, MESSAGE: text}


@Log(show_params=False)
def read_requests(r_clients, all_clients):
    ''' Чтение запросов из списка клиентов
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
                        send_message(sock, message)
                    else:
                        # Нам прислали неверный тип
                        raise TypeError
            print(data)
        except:
            print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
            all_clients.remove(sock)

    return responses


@Log(show_params=False)
def write_responses(requests, w_clients, all_clients):
    ''' Эхо-ответ сервера клиентам, от которых были запросы
    '''

    for sock in w_clients:
        if sock in requests:
            try:
                # формируем ответ
                response = presence_response(bytes_to_dict(requests[sock].encode('utf-8')))
                # отправляем ответ клиенту
                send_message(sock, response)
            except:                 # Сокет недоступен, клиент отключился
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                sock.close()
                all_clients.remove(sock)


def mainloop():
    ''' Основной цикл обработки запросов клиентов
    '''
    clients = []

    server = socket(AF_INET, SOCK_STREAM)
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

    server.bind((addr, port))
    server.listen(100)
    server.settimeout(0.2)   # Таймаут для операций с сокетом
    while True:
        # print('В цикле')
        try:
            conn, addr = server.accept()  # Проверка подключений
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
            requests = read_requests(r, clients)      # Сохраним запросы клиентов
            write_responses(requests, w, clients)     # Выполним отправку ответов клиентам

if __name__ == '__main__':
    print('Эхо-сервер запущен!')
    mainloop()