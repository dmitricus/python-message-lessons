import hmac
import os




# -------------- Функция аутентификации клиента на сервере --------------------
def server_authenticate(connection, secret_key):
    ''' Запрос аутентификаии клиента.
        сonnection - сетевое соединение (сокет);
        secret_key - ключ шифрования, известный клиенту и серверу
    '''
    # 1. Создаётся случайное послание и отсылается клиенту
    message = os.urandom(32)
    connection.send(message)

    # 2. Вычисляется HMAC-функция от послания с использованием секретного ключа
    hash = hmac.new(secret_key, message)
    digest = hash.digest()

    # 3. Пришедший ответ от клиента сравнивается с локальным результатом HMAC
    response = connection.recv(len(digest))
    #print("Хеш от клиента: {} Хеш для сервера: {}".format(digest, response))
    return hmac.compare_digest(digest, response)


def client_authenticate(connection, secret_key):
    ''' Аутентификация клиента на удаленном сервисе.
        Параметр connection - сетевое соединение (сокет);
        secret_key - ключ шифрования, известный клиенту и серверу
    '''
    message = connection.recv(32)
    hash = hmac.new(secret_key, message)
    digest = hash.digest()
    connection.send(digest)
    #print("Хеш для сервера: {}".format(digest))