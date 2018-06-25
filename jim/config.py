"""Константы для jim протокола, настройки"""
# Ключи
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
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

# Коды ответов (будут дополняться)
BASIC_NOTICE = 100
OK = 200
ACCEPTED = 202
WRONG_REQUEST = 400  # неправильный запрос/json объект
SERVER_ERROR = 500

# Кортеж из кодов ответов
RESPONSE_CODES = (BASIC_NOTICE, OK, ACCEPTED, WRONG_REQUEST, SERVER_ERROR)

USERNAME_MAX_LENGTH = 25
MESSAGE_MAX_LENGTH = 500

ENCODING = 'utf-8'

# Кортеж действий
ACTIONS = (PRESENCE, MSG, GET_CONTACTS, CONTACT_LIST, ADD_CONTACT, DEL_CONTACT)
