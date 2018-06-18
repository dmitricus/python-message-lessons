import time as ctime
from .config import *
from .exceptions import WrongParamsError, ToLongError, WrongActionError, WrongDictError, ResponseCodeError


class MaxLengthField:
    """Дескриптор ограничивающий размер поля"""

    def __init__(self, name, max_length):
        """
        :param name: имя поля
        :param max_length: максимальная длина
        """
        self.max_length = max_length
        self.name = '_' + name

    def __set__(self, instance, value):
        # если длина поля больше максимального значения
        if len(value) > self.max_length:
            # вызываем ошибку
            raise ToLongError(self.name, value, self.max_length)
        # иначе записываем данные в поле
        setattr(instance, self.name, value)

    def __get__(self, instance, owner):
        # получаем данные поля
        return getattr(instance, self.name)


class Jim:
    def to_dict(self):
        return {}

    @staticmethod
    def try_create(jim_class, input_dict):
        try:
            #JimMessage(**input_dict)
            return jim_class(**input_dict)
        except KeyError:
            raise WrongParamsError(input_dict)


    @staticmethod
    def from_dict(input_dict):
        """Наиболее важный метод создания объекта из входного словаря
        :input_dict: входной словарь
        :return: объект Jim: Action или Response
        """
        # должно быть response или action
        # если action
        if ACTION in input_dict:
            # достаем действие
            action = input_dict.pop(ACTION)
            # действие должно быть в списке действий
            if action in ACTIONS:
                if action == PRESENCE:
                    return Jim.try_create(JimPresence, input_dict)
                elif action == MSG:
                    try:
                        input_dict['from_'] = input_dict['from']
                    except KeyError:
                        raise WrongParamsError(input_dict)
                    del input_dict['from']
                    return Jim.try_create(JimMessage, input_dict)
                elif action == GETCONTACTS:
                    return Jim.try_create(JimGetContacts, input_dict)
            else:
                raise WrongActionError(action)
        elif RESPONSE in input_dict:
            return Jim.try_create(JimResponse, input_dict)
        else:
            raise WrongDictError(input_dict)


class JimAction(Jim):
    # __slots__ = (ACTION, TIME) - со слотами не работает __dict__ - а он нам нужен для перевода в json

    def __init__(self, action, time=None):
        self.action = action
        if time:
            self.time = time
        else:
            self.time = ctime.time()

    def to_dict(self):
        result = super().to_dict()
        result[ACTION] = self.action
        result[TIME] = self.time
        return result

        # @staticmethod
        # def create_from_dict(action, input_dict):
        #     if action == PRESENCE:
        #         return JimPresence(**input_dict)
        #     elif action == MSG:
        #         return JimMessage(**input_dict)
        #     else:
        #         pass


class JimPresence(JimAction):
    # Имя пользователя ограничено 25 символов - используем дескриптор
    account_name = MaxLengthField('account_name', USERNAME_MAX_LENGTH)

    # __slots__ = (ACTION, ACCOUNT_NAME, TIME) - дескриптор конфилктует со слотами

    def __init__(self, account_name, time=None):
        self.account_name = account_name
        super().__init__(PRESENCE, time)

    def to_dict(self):
        result = super().to_dict()
        result[ACCOUNT_NAME] = self.account_name
        return result


class JimMessage(JimAction):
    # __slots__ = (ACTION, TIME, TO, FROM, MESSAGE)
    to = MaxLengthField('to', USERNAME_MAX_LENGTH)
    from_ = MaxLengthField('from', USERNAME_MAX_LENGTH)
    message = MaxLengthField('message', MESSAGE_MAX_LENGTH)

    def __init__(self, to, from_, message, time=None):
        self.to = to
        self.from_ = from_
        self.message = message
        super().__init__(MSG, time=time)

    def to_dict(self):
        result = super().to_dict()
        result[TO] = self.to
        result[FROM] = self.from_
        result[MESSAGE] = self.message
        return result


class ResponseField:
    def __init__(self, name):
        """
        :param name: имя поля
        """
        self.name = '_' + name

    def __set__(self, instance, value):
        # если значение кода не входит в список доступных котов
        if value not in RESPONSE_CODES:
            # вызываем ошибку
            raise ResponseCodeError(value)
        # иначе записываем данные в поле
        setattr(instance, self.name, value)

    def __get__(self, instance, owner):
        # получаем данные поля
        return getattr(instance, self.name)


class JimResponse(Jim):
    # __slots__ = (RESPONSE, ERROR, ALERT)
    # Используем дескриптор для поля ответ от сервера
    response = ResponseField('response')

    def __init__(self, response, error=None, alert=None):
        self.response = response
        self.error = error
        self.alert = alert

    def to_dict(self):
        result = super().to_dict()
        result[RESPONSE] = self.response
        if self.error:
            result[ERROR] = self.error
        if self.alert:
            result[ALERT] = self.alert
        return result

# Запрос списка контактов у сервера
class JimGetContacts(JimAction):
    # Имя пользователя ограничено 25 символов - используем дескриптор
    account_name = MaxLengthField('account_name', USERNAME_MAX_LENGTH)

    # __slots__ = (ACTION, ACCOUNT_NAME, TIME) - дескриптор конфилктует со слотами

    def __init__(self, account_name, time=None):
        self.account_name = account_name
        super().__init__(GETCONTACTS, time)

    def to_dict(self):
        result = super().to_dict()
        result[ACCOUNT_NAME] = self.account_name
        return result

# Ответ сервера клиенту успех или ошибка запроса
class JimResponseGetContacts(Jim):
    # __slots__ = (RESPONSE, ERROR, ALERT)
    # Используем дескриптор для поля ответ от сервера
    response = ResponseField('response')

    def __init__(self, response, quantity=None, error=None, alert=None):
        self.response = response
        self.quantity = quantity
        self.error = error
        self.alert = alert

    def to_dict(self):
        result = super().to_dict()
        result[RESPONSE] = self.response
        result[QUANTITY] = self.quantity
        if self.error:
            result[ERROR] = self.error
        if self.alert:
            result[ALERT] = self.alert
        return result

# Формируем ответ клиенту о контактах
class JimContactsList(JimAction):
    # Имя пользователя ограничено 25 символов - используем дескриптор
    user_id = MaxLengthField('user_id', USERNAME_MAX_LENGTH)

    # __slots__ = (ACTION, ACCOUNT_NAME, TIME) - дескриптор конфилктует со слотами

    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(CONTACTLIST)

    def to_dict(self):
        result = super().to_dict()
        result[USERID] = self.user_id
        return result

# Запрос на добавление контакта
class JimAddContacts(JimAction):
    # Имя пользователя ограничено 25 символов - используем дескриптор
    user_id = MaxLengthField('user_id', USERNAME_MAX_LENGTH)

    # __slots__ = (ACTION, ACCOUNT_NAME, TIME) - дескриптор конфилктует со слотами

    def __init__(self, user_id, time=None):
        self.user_id = user_id
        super().__init__(ADDCONTACT, time)

    def to_dict(self):
        result = super().to_dict()
        result[USERID] = self.user_id
        return result

# Запрос на удаление контакта
class JimDelContacts(JimAction):
    # Имя пользователя ограничено 25 символов - используем дескриптор
    account_name = MaxLengthField('account_name', USERNAME_MAX_LENGTH)

    # __slots__ = (ACTION, ACCOUNT_NAME, TIME) - дескриптор конфилктует со слотами

    def __init__(self, account_name, time=None):
        self.account_name = account_name
        super().__init__(DELCONTACT, time)

    def to_dict(self):
        result = super().to_dict()
        result[ACCOUNT_NAME] = self.account_name
        return result

# Ответ сервера клиенту успех или ошибка запроса
class JimResponseAddContacts(Jim):
    # __slots__ = (RESPONSE, ERROR, ALERT)
    # Используем дескриптор для поля ответ от сервера
    response = ResponseField('response')

    def __init__(self, response, quantity=None, error=None, alert=None):
        self.response = response
        self.quantity = quantity
        self.error = error
        self.alert = alert

    def to_dict(self):
        result = super().to_dict()
        result[RESPONSE] = self.response
        result[QUANTITY] = self.quantity
        if self.error:
            result[ERROR] = self.error
        if self.alert:
            result[ALERT] = self.alert
        return result

# Ответ сервера клиенту успех или ошибка запроса
class JimResponseDelContacts(Jim):
    # __slots__ = (RESPONSE, ERROR, ALERT)
    # Используем дескриптор для поля ответ от сервера
    response = ResponseField('response')

    def __init__(self, response, quantity=None, error=None, alert=None):
        self.response = response
        self.quantity = quantity
        self.error = error
        self.alert = alert

    def to_dict(self):
        result = super().to_dict()
        result[RESPONSE] = self.response
        result[QUANTITY] = self.quantity
        if self.error:
            result[ERROR] = self.error
        if self.alert:
            result[ALERT] = self.alert
        return result