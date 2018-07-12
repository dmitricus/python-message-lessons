from logging_message.client_log_config import *
# inspect - стандартный модуль для для сбора информации о существующих объектах
# ( имена  и значения атрибутов, строки документирования,
# исходный программный код, кадры стеков и прочее)
import inspect
# wraps служит, чтобы переопределить внутренние атрибуты декоратора
# атрибутами декорируемой  функции  (__doc__, __name__)
from functools import wraps

# декоратор
class Log:
    """
        Декоратор для логгирования декорируемой функции
    """
    def __init__(self, logger):
        # запоминаем логгер, чтобы можно было использовать разные
        self.logger = logger

    @staticmethod
    def _create_message(result=None, *args, **kwargs):
        """
        Формирует сообщение для записи в лог
        :param result: результат работы функции
        :param args: любые параметры по порядку
        :param kwargs: любые именованные параметры
        :return:
        """
        message = ''
        if args:
            message += 'args: {} '.format(args)
        if kwargs:
            message += 'kwargs: {} '.format(kwargs)
        if result:
            message += '= {}'.format(result)
        # Возвращаем итоговое сообщение
        return message

    def __call__(self, func):
        """
        Определяем __call__ для возможности вызова экземпляра как декоратора
        :param func: функция которую будем декорировать
        :return: новая функция
        """
        @wraps(func)
        def decorated(*args, **kwargs):
            #console = logging.StreamHandler()
            #console.setLevel(logging.DEBUG)
            #console.setFormatter(formatter)
            #logger.addHandler(console)

            # Выполняем функцию и получаем результат
            result = func(*args, **kwargs)
            # Формируем сообщение в лог
            message = Log._create_message(result, *args, **kwargs)

            # Получаем стековый фрейм текущей  функции :
            curframe = inspect.currentframe()
            # Получаем список записей из текущего кадра стека и всех объемлющих кадров.
            # Каждая запись является кортежем из 6 элементов (frame, filename, lineno, funcname, code_context, index)
            callframe = inspect.getouterframes(curframe, 2)
            # В логгирование передаем имя текущей функции и имя вызвавшей функции
            self.logger.info('Функция {} вызвана из функции {}'.format(func.__name__, callframe[1][3]))


            # Пишем сообщение в лог
            # Хотя мы и подменили с помощью wraps имя и модуль для внутренней функции,
            # логгер всё равно берет не те, поэтому приходиться делать через decorated.__name__, !
            self.logger.debug('{} - {} - {}'.format(message, decorated.__name__, decorated.__module__))

            return result

        # в результате новая функция
        return decorated

@Log
def usefull_func():
    print('Тестовая функция')
    return True


def main():
    # Очистим все обработчики событий
    server_logger.handlers = []

    # Создадим обработчит только для этого модуля
    fh = logging.FileHandler('../logs/app.main.log', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    server_logger.addHandler(fh)

    print("Запущен внутренний модуль логгирования")
    usefull_func()


if __name__ == '__main__':
    main()