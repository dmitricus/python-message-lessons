import json
from logging_message.log_util import Log
from jim.config import *

import logging
# Получаем по имени клиентский логгер, он уже нестроен в log_config

# Кодировка
ENCODING = 'utf-8'


def dict_to_bytes(message_dict):
    """
    Преобразование словаря в байты
    :param message_dict: словарь
    :return: bytes
    """
    # Проверям, что пришел словарь
    if isinstance(message_dict, dict) or isinstance(message_dict, list):
        # Преобразуем словарь в json
        jmessage = json.dumps(message_dict)
        # Переводим json в байты
        bmessage = jmessage.encode(ENCODING)
        # Шифруем сообщение
        #encrypted_text = encrypted_msg(bmessage, cipher_key)
        # Возвращаем байты
        #print(encrypted_text)
        return bmessage
    else:
        raise TypeError


def bytes_to_dict(message_bytes):
    """
    Получение словаря из байтов
    :param message_bytes: сообщение в виде байтов
    :return: словарь сообщения
    """
    # Если переданы байты
    #print('Пришли байты', message_bytes)
    if isinstance(message_bytes, bytes):
        # Расшифруем сообщение
        #decrypt_text = decrypted_msg(message_bytes, cipher_key)
        #print(decrypt_text)
        # Декодируем
        jmessage = message_bytes.decode(ENCODING)
        # Из json делаем словарь
        message = json.loads(jmessage)
        # Если там был словарь
        if isinstance(message, dict) or isinstance(message, list):
            # Возвращаем сообщение
            return message
        else:
            # Нам прислали неверный тип
            raise TypeError
    else:
        # Передан неверный тип
        raise TypeError


def send_message(sock, message):
    """
    Отправка сообщения
    :param sock: сокет
    :param message: словарь сообщения
    :return: None
    """
    try:
        # Словарь переводим в байты
        bprescence = dict_to_bytes(message)
        # Отправляем
        sock.send(bprescence)
    except Exception as e:
        print("Ошибка в функции utils.send_message:", e)


def get_message(sock):
    """
    Получение сообщения
    :param sock:
    :return: словарь ответа
    """
    try:
        # Получаем байты
        bresponse = sock.recv(1024)
        #bresponse = sock.recv(4096)
        # переводим байты в словарь
        if bresponse:
            response = bytes_to_dict(bresponse)
            # возвращаем словарь
            return response
    except Exception as e:
        print("Ошибка в функции utils.get_message:", e)




