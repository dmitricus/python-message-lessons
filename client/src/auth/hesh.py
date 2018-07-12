import hashlib, uuid
import hmac
from jim.config import *


# Хеширует сообщение
def hash_decode(message, secret_key):
    '''
        secret_key - ключ шифрования, известный клиенту и серверу
    '''

    hash = hmac.new(secret_key, message)
    digest = hash.digest()
    return digest

# Расшифровка сообщения
def hash_encode(message, secret_key):
    '''
        secret_key - ключ шифрования, известный клиенту и серверу
    '''

    hash = hmac.new(secret_key, message)
    digest = hash.digest()
    return digest

def hash(password, salt):
    hashed_password = hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
    return hashed_password

#salt = uuid.uuid4().bytes
#salt = "5b0d3d7f5f644ed0aa82be121851c07f"
#password = "12345"
#print(salt)
#hashed_password = hash(password, salt)
#print(hashed_password)