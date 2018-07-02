import sys
import os
import socket
from client import User
from db.server_models import session
from db.server_controller import Storage
from db.server_errors import ContactDoesNotExist
from chat_controller import GuiReceiver
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QThread, pyqtSlot, pyqtSignal

dir = os.path.abspath(os.path.dirname(__file__))

# Класс ГрафическийЧат - базовый класс, реализующий интерфейс пользователя (UI) - вывод сообщений чата,
# ввод данных от пользователя - служит базой для разных интерфейсов пользователя (консольный, графический, WEB).
class GraphicChat(QtWidgets.QMainWindow):
    sentData = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(dir + '/gui/ui/', 'client_chat.ui'), self)

    def stop_chat(self):
        ''' Остановка входящих соединений '''
        if self.receiver is not None:
            self.receiver.stop()

    def finished(self):
        ''' Действия при отключении
        '''
        self.receiver.stop()
        client.disconnect()

    def load_contacts(self, contacts):
        """получение списка контактов"""
        # Чистим список
        window.listWidgetContacts.clear()
        # Добавим
        for contact in contacts:
            window.listWidgetContacts.addItem(str(contact))

    def add_contact(self):
        """Добавление контакта"""
        # Получаем имя из QTextEdit
        try:
            username = window.textEditUsername.toPlainText()
            if username:
                # Соединение
                #client.connect()
                client.add_contact(username)
                window.listWidgetContacts.addItem(username)
                window.textEditUsername.clear()
                # отключаемся
                #client.disconnect()
        except Exception as e:
            print(e)

    def del_contact(self):
        try:
            current_item = window.listWidgetContacts.currentItem()
            username = current_item.text()
            # Соединение
            #client.connect()
            client.del_contact(username)
            # отключаемся
            #client.disconnect()
            current_item = window.listWidgetContacts.takeItem(window.listWidgetContacts.row(current_item))
            del current_item
        except Exception as e:
            print(e)

    def send_message(self):
        text = window.textEditMessage.toPlainText()
        if text:
            try:
                selected_index = window.listWidgetContacts.currentIndex()
                if selected_index:
                    user_name = selected_index.data()
                    # Соединение
                    #client.connect()
                    #print("Подключаюсь к серверу")
                    client.send_message(user_name, text)
                    # отключаемся
                    #client.disconnect()
                    #print("Отключаюсь от сервера")
                    msg = ' {}: {}'.format(name, text)
                    window.listWidgetMessages.addItem(msg)
                window.textEditMessage.clear()
            except Exception as e:
                print(e)

    def setGuiConnected(self, enabled):
        ''' Настройка GUI при подключении/отключении
        '''
        window.listWidgetMessages.setEnabled(enabled)
        window.textEditMessage.setEnabled(enabled)
        window.pushButtonSend.setEnabled(enabled)
        window.clearTextButton.setEnabled(enabled)
        window.connectButton.setEnabled(not enabled)
        window.disconnectButton.setEnabled(enabled)


def finished(receiver):
    ''' Действия при отключении
    '''
    receiver.stop()
    window.setGuiConnected(False)
    client.disconnect()

def stop_chat(receiver):
    ''' Остановка входящих соединений '''
    if receiver is not None:
        receiver.stop()

def clear_text():
    window.listWidgetMessages.clear()

def start_chat():
    window.setGuiConnected(True)
    client.connect()
    receiver = GuiReceiver(client.sock, client.request_queue)
    receiver.gotData.connect(update_chat)

    # Создание потока и помещение объекта-монитора в этот поток
    thread = QThread()
    receiver.moveToThread(thread)

    # ---------- Важная часть - связывание сигналов и слотов ----------
    # При запуске потока будет вызван метод search_text
    thread.started.connect(receiver.poll)

    # При завершении поиска необходимо завершить поток и изменить GUI
    receiver.finished.connect(thread.quit)
    receiver.finished.connect(window.finished)

    # Запуск потока, который запустит self.monitor.search_text
    thread.start()

    contact_list = client.get_contacts()

    # грузим контакты в список сразу при запуске приложения
    window.load_contacts(contact_list)

@pyqtSlot(str)
def update_chat(data):
    try:
        msg = data
        window.listWidgetMessages.addItem(msg)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    try:
        addr = sys.argv[1]
    except IndexError:
        addr = 'localhost'
    try:
        port = int(sys.argv[2])
    except IndexError:
        port = 7777
    except ValueError:
        print('Порт должен быть целым числом')
        sys.exit(0)
    try:
        name = sys.argv[3]
        print(name)
    except IndexError:
        name = 'Dmitricus'

    app = QtWidgets.QApplication(sys.argv)
    client = User(name, addr, port)
    window = GraphicChat()

    window.setWindowTitle("Мессенджер - {}".format(name))
    window.pushButtonAddContact.clicked.connect(window.add_contact)
    window.pushButtonDelContact.clicked.connect(window.del_contact)
    window.connectButton.clicked.connect(start_chat)
    window.disconnectButton.clicked.connect(finished)
    window.pushButtonSend.clicked.connect(window.send_message)
    window.clearTextButton.clicked.connect(clear_text)
    window.show()
    sys.exit(app.exec_())