
# ---- Пример настройки логгирования для приложения, используя logging ----

# * Logging Cookbook: https://docs.python.org/3/howto/logging-cookbook.html

# logging - стандартный модуль для организации логгирования
import logging
import logging.handlers
import os

# Папка где лежит этот файл
LOG_FOLDER_PATH = os.path.abspath(os.path.dirname(__file__))
# Пусть до серверного лога
#SERVER_LOF_FILE_PATH = os.path.join(LOG_FOLDER_PATH, 'server.log')
SERVER_LOF_FILE_PATH = os.path.join(LOG_FOLDER_PATH + "/logs/", 'server.log')

# Быстрая настройка логгирования может быть выполнена так:
# logging.basicConfig(filename="gui.logging_message",
#     format="%(levelname)-10s %(asctime)s %(message)s",
#     level = logging.INFO
# )

# Можно выполнить более расширенную настройку логгирования.
# Создаем логгер с именем server
server_logger = logging.getLogger('server')
# Формат сообщения
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s ", datefmt='%d.%m.%Y %H:%M:%S')

# Возможные настройки для форматирования:
# -----------------------------------------------------------------------------
# | Формат         | Описание
# -----------------------------------------------------------------------------
# | %(name)s       | Имя регистратора.
# | %(levelno)s    | Числовой уровень важности.
# | %(levelname)s  | Символическое имя уровня важности.
# | %(pathname)s   | Путь к исходному файлу, откуда была выполнена запись в журнал.
# | %(filename)s   | Имя исходного файла, откуда была выполнена запись в журнал.
# | %(funcName)s   | Имя функции, выполнившей запись в журнал.
# | %(module)s     | Имя модуля, откуда была выполнена запись в журнал.
# | %(lineno)d     | Номер строки, откуда была выполнена запись в журнал.
# | %(created)f    | Время, когда была выполнена запись в журнал. Значением
# |                | должно быть число, такое как возвращаемое функцией time.time().
# | %(asctime)s    | Время в формате ASCII, когда была выполнена запись в журнал.
# | %(msecs)s      | Миллисекунда, когда была выполнена запись в журнал.
# | %(thread)d     | Числовой идентификатор потока выполнения.
# | %(threadName)s | Имя потока выполнения.
# | %(process)d    | Числовой идентификатор процесса.
# | %(message)s    | Текст журналируемого сообщения (определяется пользователем).
# -----------------------------------------------------------------------------


# Ротация логов
# -----------------------------------------------------------------------------
# | Значение        | Тип интервала
# -----------------------------------------------------------------------------
# | 'S'	            | секунд
# | 'M'		        | Протокол
# | 'H'		        | Несколько часов
# | 'D'		        | Дни
# | 'W0'-'W6'		| Будний День (0 = Понедельник)
# | 'midnight' 	    | в полночь
# -----------------------------------------------------------------------------


# Создаём файловый обработчик логгирования (можно задать кодировку):
# Ротация логов раз в день
server_handler = logging.handlers.TimedRotatingFileHandler(SERVER_LOF_FILE_PATH, when='D', interval=1, backupCount=0, encoding='utf-8')
server_handler.setFormatter(formatter)


# Добавляем в логгер новый обработчик событий и устанавливаем уровень логгирования
server_logger.addHandler(server_handler)
server_logger.setLevel(logging.INFO)

# Возможные уровни логгирования:
# -----------------------------------------------------------------------------
# | Уровень важности | Использование
# -----------------------------------------------------------------------------
# | CRITICAL         | logging_message.critical(fmt [, *args [, exc_info [, extra]]])
# | ERROR            | logging_message.error(fmt [, *args [, exc_info [, extra]]])
# | WARNING          | logging_message.warning(fmt [, *args [, exc_info [, extra]]])
# | INFO             | logging_message.info(fmt [, *args [, exc_info [, extra]]])
# | DEBUG            | logging_message.debug(fmt [, *args [, exc_info [, extra]]])
# -----------------------------------------------------------------------------



if __name__ == '__main__':
    # Создаём потоковый обработчик логгирования (по умолчанию sys.stderr):
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    server_logger.addHandler(console)
    # В логгирование передаем имя текущей функции и имя вызвавшей функции
    server_logger.info('Тестовый запуск логгирования')
