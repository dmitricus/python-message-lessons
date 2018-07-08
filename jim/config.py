"""Константы для jim протокола, настройки"""
# Ключи
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
PASSWORD = 'password'
USER_ID = 'user_id'
RESPONSE = 'response'
ERROR = 'error'
ALERT = 'alert'
QUANTITY = 'quantity'

# Значения
PRESENCE = 'presence'
MSG = 'msg'
TO = 'to'
FROM = 'from'
MESSAGE = 'message'
GET_CONTACTS = 'get_contacts'
CONTACT_LIST = 'contact_list'
ADD_CONTACT = 'add_contact'
DEL_CONTACT = 'del_contact'
PUBKEY = 'pubkey'
PUBLIC_KEY = 'public_key'


# Коды ответов (будут дополняться)
BASIC_NOTICE = 100
OK = 200
ACCEPTED = 202
WRONG_REQUEST = 400  # неправильный запрос/json объект
SERVER_ERROR = 500
UNAUTHORIZED = 401  # не авторизован (не представился)
NOTFOUND = 404  # не найдено
WRONG_LOGIN = 111.4  # Неверный логин
WRONG_PASSWORD = 111.5   # Неверный пароль



# Кортеж из кодов ответов
RESPONSE_CODES = (BASIC_NOTICE, OK, ACCEPTED, WRONG_REQUEST, SERVER_ERROR, UNAUTHORIZED, WRONG_LOGIN, WRONG_PASSWORD)

USERNAME_MAX_LENGTH = 25
MESSAGE_MAX_LENGTH = 500

ENCODING = 'utf-8'

# Кортеж действий
ACTIONS = (PRESENCE, MSG, PUBKEY, GET_CONTACTS, CONTACT_LIST, ADD_CONTACT, DEL_CONTACT)

secret_key = b'our_secret_key'
salt = '5b0d3d7f5f644ed0aa82be121851c07f'
cipher_key = b'k_q-kAIwdDmclgw2yFUJPp3MGrrIwvYGrPnVRjHhN2k='