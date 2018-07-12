# Служебный скрипт запуска/останова нескольких клиентских приложений

from subprocess import Popen, CREATE_NEW_CONSOLE
import time
import os
from server.src.db.server_models import session
from server.src.db.server_controller import Storage

dir = os.path.abspath(os.path.dirname(__file__))
# список запущенных процессов
p_list = []
storage = Storage(session)



while True:
    user = input("Запустить сервер и клиентов (s) / Выйти (q)")

    if user == 's':
        # запускаем сервер
        # Запускаем серверный скрипт и добавляем его в список процессов
        #p_list.append(Popen('python server.py'.format(SERVER_FILE_PATH),
                            #creationflags=CREATE_NEW_CONSOLE))
        #print('Сервер запущен')
        # ждем на всякий пожарный
        time.sleep(1)
        # Получаем всех клиетов
        clients = storage.get_clients()

        for client in clients:
            # Запускаем клиентский скрипт и добавляем его в список процессов
            p_list.append(Popen('python graphic_chat.py localhost 7777 {} 12345'.format(client.Name)))
        print('Клиенты запущены')
        # запускаем клиента на запись случайное число
        #for _ in range(2):
            # Запускаем клиентский скрипт и добавляем его в список процессов
         #   p_list.append(Popen('python client.py localhost 7777 w',
         #                       creationflags=CREATE_NEW_CONSOLE))
        #print('Клиенты на запись запущены')
    elif user == 'q':
        print('Открыто процессов {}'.format(len(p_list)))
        for p in p_list:
            print('Закрываю {}'.format(p))
            p.kill()
        p_list.clear()
        print('Выхожу')
        break