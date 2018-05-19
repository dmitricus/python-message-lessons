import json
from logging_message.log_util import *

# Кодировка
ENCODING = 'utf-8'


# словарь в json
@Log(show_params=False)
def dict_to_bytes(message_dict):
    """
    Преобразование словаря в байты
    :param message_dict: словарь
    :return: bytes
    """
    # Проверям, что пришел словарь
    if isinstance(message_dict, dict):
        # Преобразуем словарь в json
        jmessage = json.dumps(message_dict)
        # Переводим json в байты
        bmessage = jmessage.encode(ENCODING)
        # Возвращаем байты
        return bmessage
    elif isinstance(message_dict, json):
        # Переводим json в байты
        bmessage = message_dict.encode(ENCODING)
        # Возвращаем байты
        return bmessage
    else:
        raise TypeError

@Log(show_params=False)
def bytes_to_dict(message_bytes):
    """
    Получение словаря из байтов
    :param message_bytes: сообщение в виде байтов
    :return: словарь сообщения
    """
    # Если переданы байты
    if isinstance(message_bytes, bytes):
        if message_bytes:
            # Декодируем
            jmessage = message_bytes.decode(ENCODING)
            # Из json делаем словарь
            message = json.loads(jmessage)
            #print(message)
            # Если там был словарь
            if isinstance(message, dict):
                # Возвращаем сообщение
                return message
            else:
                # Нам прислали неверный тип
                raise TypeError
        else:
            print("Пустое сообщение!")
    else:
        # Передан неверный тип
        raise TypeError

@Log(show_params=False)
def send_message(sock, message):
    """
    Отправка сообщения
    """
    # Словарь переводим в байты
    bprescence = dict_to_bytes(message)
    # Отправляем
    sock.send(bprescence)

@Log(show_params=False)
def get_message(sock):
    """
    Получение сообщения
    """
    # Получаем байты
    bresponse = sock.recv(1024)
    # переводим байты в словарь
    response = bytes_to_dict(bresponse)
    # возвращаем словарь
    return response

@Log(show_params=False)
def get_messages(r_clients, all_clients):
    ''' Чтение запросов из списка клиентов
    '''
    responses = {}      # Словарь ответов сервера вида {сокет: запрос}

    for sock in r_clients:
        try:
            data = sock.recv(1024)
            data = bytes_to_dict(data)
            responses[sock] = data
        except:
            print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
            all_clients.remove(sock)

    return responses

@Log(show_params=False)
def send_messages(requests, resp_message, w_clients, all_clients):
    ''' Ответ сервера клиентам, от которых были запросы
    '''

    for sock in w_clients:
        if sock in requests:
            try:
                # Подготовить и отправить ответ сервера
                presence = requests[sock]
                response = resp_message(presence)
                response = bytes_to_dict(response)
                sock.sendall(response)
            except:                 # Сокет недоступен, клиент отключился
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                sock.close()
                all_clients.remove(sock)