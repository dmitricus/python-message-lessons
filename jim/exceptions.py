class WrongInputError(Exception):
    pass


class WrongParamsError(WrongInputError):
    """Неверные параметры для действия"""

    def __init__(self, params):
        self.params = params

    def __str__(self):
        return 'Wrong action params: {}'.format(self.params)


class WrongActionError(WrongInputError):
    """Когда передано неверное действие"""

    def __init__(self, action):
        self.action = action

    def __str__(self):
        return 'Wrong action: {}'.format(self.action)


class WrongDictError(WrongInputError):
    """Когда пришел неправильный словарь"""

    def __init__(self, input_dict):
        self.input_dict = input_dict

    def __str__(self):
        return 'Wrong input dict: {}'.format(self.input_dict)


class ToLongError(Exception):
    """Ошибка когда наше поле длинее чем надо"""

    def __init__(self, name, value, max_length):
        """
        :param name: имя поля
        :param value: текущее значение
        :param max_length: максимальное значение
        """
        self.name = name
        self.value = value
        self.max_length = max_length

    def __str__(self):
        return '{}: {} to long (> {} simbols)'.format(self.name, self.value, self.max_length)


class ResponseCodeError(Exception):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return 'Wrong response code: {}'.format(self.code)
