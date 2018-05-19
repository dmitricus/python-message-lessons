from logging_message.log_config import *
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
    def __init__(self, show_params=True):
        self.show_params = show_params

    def __call__(self, old_func):
        # внутри объявляем новую функцию которая будет вместо старой
        @wraps(old_func)
        def decorated(*args, **kwargs):
            #console = logging.StreamHandler()
            #console.setLevel(logging.DEBUG)
            #console.setFormatter(formatter)
            #logger.addHandler(console)

            # Получаем стековый фрейм текущей  функции :
            curframe = inspect.currentframe()

            # Получаем список записей из текущего кадра стека и всех объемлющих кадров.
            # Каждая запись является кортежем из 6 элементов (frame, filename, lineno, funcname, code_context, index)
            callframe = inspect.getouterframes(curframe, 2)

            # В логгирование передаем имя текущей функции и имя вызвавшей функции
            logger.info('Функция {} вызвана из функции {}'.format(old_func.__name__, callframe[1][3]))

            if self.show_params:
                print('Параметры:', args)
                print('Параметры по имени:', kwargs)

            # вызываем старую функцию
            result = old_func(*args, **kwargs)
            return result

        # в результате новая функция
        return decorated

@Log(show_params=False)
def usefull_func():
    print('Тестовая функция')
    return True


def main():
    # Очистим все обработчики событий
    logger.handlers = []

    # Создадим обработчит только для этого модуля
    fh = logging.FileHandler('../logs/app.main.log', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    print("Запущен внутренний модуль логгирования")
    usefull_func()


if __name__ == '__main__':
    main()