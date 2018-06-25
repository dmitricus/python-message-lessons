from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
import sys
import os
from db.server_models import session
from db.server_controller import Storage

app = QtWidgets.QApplication(sys.argv)
dir = os.path.abspath(os.path.dirname(__file__))
window = uic.loadUi(os.path.join(dir +'/ui/', 'server_monitor.ui'))
storage = Storage(session)


def load_clients():
    """загрузчик клиентов в QListWidget"""
    # Получаем всех клиетов
    clients = storage.get_clients()
    # Чистим список
    window.listWidgetClients.clear()
    # добавляем
    i = 0
    for client in clients:
        i += 1
        window.listWidgetClients.addItem('{} # {}'.format(i, client.Name))

def load_history():
    """ загрузка истории в QListWidget """
    # Получаем все истории
    histories = storage.get_histories()
    # Чистим список
    window.listWidgetHistory.clear()
    # добавляем
    for history in histories:
        window.listWidgetHistory.addItem(str(history))


def refresh():
    """Обновить все"""
    load_clients()


# Сразу все грузим при запуске скрипта
refresh()

# Связываем меню сигнала triggered - нажатие и слот функцию refresh
window.actionrefresh.triggered.connect(refresh)

# рисуем окно
window.show()
# точка входа в приложение
sys.exit(app.exec_())
