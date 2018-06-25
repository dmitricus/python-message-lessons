from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QThread, pyqtSlot
from client import User
import sys
import os
from client import User
from db.server_models import session
from db.server_controller import Storage
from db.server_errors import ContactDoesNotExist

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
dir = os.path.abspath(os.path.dirname(__file__))
window = uic.loadUi(os.path.join(dir +'/ui/', 'client_chat.ui'))

client = User(name, addr, port)
client.connect()
contact_list = client.get_contacts()
#client.disconnect()
window.setWindowTitle("Мессенджер - {}".format(name))


def load_contacts(contacts):
    """получение списка контактов"""
    # Чистим список
    window.listWidgetContacts.clear()
    # Добавим
    for contact in contacts:
        window.listWidgetContacts.addItem(str(contact))

# грузим контакты в список сразу при запуске приложения
load_contacts(contact_list)


def add_contact():
    """Добавление контакта"""
    # Получаем имя из QTextEdit
    try:
        username = window.textEditUsername.toPlainText()
        if username:
            # Соединение
            client.add_contact(username)
            window.listWidgetContacts.addItem(username)
            window.textEditUsername.clear()
    except Exception as e:
        print(e)

window.pushButtonAddContact.clicked.connect(add_contact)

def del_contact():
    try:
        current_item = window.listWidgetContacts.currentItem()
        username = current_item.text()
        client.del_contact(username)
        current_item = window.listWidgetContacts.takeItem(window.listWidgetContacts.row(current_item))
        del current_item
    except Exception as e:
        print(e)


def send_message():
    text = window.textEditMessage.toPlainText()
    if text:
        try:
            selected_index = window.listWidgetContacts.currentIndex()
            user_name = selected_index.data()
            client.send_message(user_name, text)
            msg = '{:>10}: {}'.format(name, text)
            window.listWidgetMessages.addItem(msg)
            window.textEditMessage.clear()
        except Exception as e:
            print(e)

window.pushButtonDelContact.clicked.connect(del_contact)
window.pushButtonSend.clicked.connect(send_message)

# рисуем окно
window.show()
# точка входа в приложение
sys.exit(app.exec_())