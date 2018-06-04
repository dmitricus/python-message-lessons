from socket import socket, AF_INET, SOCK_STREAM
from client import Client
from jim.jim_class import JIMReply, JIMMessage
from jim.config import *

client = Client()

client_socket = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
addr = 'localhost'
port = 7777
mode = 'w'
# Соединиться с сервером
client_socket.connect((addr, port))
# Создаем сообщение
presence = client.create_presence()
# Отсылаем сообщение
client.send_message(client_socket, presence)
# Получаем ответ
response = client.get_message(client_socket)
# Проверяем ответ
response = client.translate_response(response)
if response['response'] == OK:
    # в зависимости от режима мы будем или слушать или отправлять сообщения
    if mode == 'r':
        client.read_messages()
    elif mode == 'w':
        client.write_messages()
    else:
        raise Exception('Не верный режим чтения/записи')