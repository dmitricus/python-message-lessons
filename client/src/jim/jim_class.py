import json
from logging_message.log_util import *
from jim.utils import bytes_to_dict, dict_to_bytes

# Класс JIMСообщение - класс, реализующий сообщение (msg) по протоколу JIM.
class JIMMessage:

    def get_message(self, sock):
        """
        Получение сообщения
        """
        # Получаем байты
        bresponse = sock.recv(1024)
        # переводим байты в словарь
        response = bytes_to_dict(bresponse)
        # возвращаем словарь
        return response


# Класс JIMОтвет - класс, реализующий ответ (response) по протоколу JIM.
class JIMReply:

    def send_message(self, sock, message):
        """
        Отправка сообщения
        """
        # Словарь переводим в байты
        bprescence = dict_to_bytes(message)
        # Отправляем
        sock.send(bprescence)

    def send_messages(self, requests, resp_message, w_clients, all_clients):
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
                except:  # Сокет недоступен, клиент отключился
                    print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                    sock.close()
                    all_clients.remove(sock)


