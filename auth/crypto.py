from cryptography.fernet import Fernet
import rsa
# Генерация ключа
#cipher_key = Fernet.generate_key()
#print(cipher_key)

# Библиотека cryptography для шифрования запросов от клиента к серверу и обратно
# Шифрование сообщения
def encrypted_msg(text, cipher_key):
    cipher = Fernet(cipher_key)
    encrypted_text = cipher.encrypt(text)
    return encrypted_text

# Расшифровка сообщения
def decrypted_msg(encrypted_text, cipher_key):
    cipher = Fernet(cipher_key)
    decrypted_text = cipher.decrypt(encrypted_text)
    return decrypted_text


if __name__ == '__main__':
    # Библиотека rsa для шифрования сообщений пользователя перед отправкой другому контакту
    #Пользователь 1 формирует публичный и секретный ключ

    (user_pub, user_priv) = rsa.newkeys(512)

    #Пользователь 2 формирует сообщение Пользователю 1 и кодирует его в UTF8,
    #поскольку RSA работает только с байтами
    message = 'hello User 1!'.encode('utf8')

    #Пользователь 2 шифрует сообщение публичным ключом Пользователя 1
    crypto = rsa.encrypt(message, user_pub)
    print(crypto.decode("ISO-8859-1"))

    #Пользователь 1 расшифровывает сообщение своим секретным ключом
    message = rsa.decrypt(crypto, user_priv)
    print(message.decode('utf8'))