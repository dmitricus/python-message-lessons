import sys
import os
import rsa
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QWidget, QMessageBox, QLabel, QVBoxLayout, QStackedLayout, QHBoxLayout, QFileDialog
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
from jim.config import *
from client import User
from gui.authenticate_dialog import AuthenticateDialog
from chat_controller import GuiReceiver

dir = os.path.abspath(os.path.dirname(__file__))



# Класс ГрафическийЧат - базовый класс, реализующий интерфейс пользователя (UI) - вывод сообщений чата,
# ввод данных от пользователя - служит базой для разных интерфейсов пользователя (консольный, графический, WEB).
class GraphicChat(QtWidgets.QMainWindow):
    sentData = pyqtSignal(str)
    def __init__(self, name, password, parent=None):
        super().__init__(parent)
        self.package_dir = os.path.abspath(os.path.dirname(__file__))
        self.ui_path = os.path.join(dir + '/gui/ui/', 'client_chat.ui')
        self.window = uic.loadUi(self.ui_path)
        self.vbar = self.window.listWidgetMessages.verticalScrollBar()
        self.name = name
        self.password = password

        # список лэйаутов чата вида 'contact':[index, QVBoxLayout].
        # Каждому контакту свой лэйаут
        self.chat_stackedLayout = QStackedLayout()
        self.chat_layout_indexes = {}

        self.init_ui()

    def init_ui(self):
        self.window.pushButtonAddContact.clicked.connect(self.add_contact)
        self.window.pushButtonDelContact.clicked.connect(self.del_contact)
        self.window.connectButton.clicked.connect(self.start_chat)
        self.window.disconnectButton.clicked.connect(self.finished)
        self.window.pushButtonSend.clicked.connect(self.send_message)
        self.window.clearTextButton.clicked.connect(self.clear_text)
        self.window.show()

    def stop_chat(self):
        ''' Остановка входящих соединений '''
        if self.receiver is not None:
            self.receiver.stop()

    def finished(self):
        ''' Действия при отключении
        '''
        self.receiver.stop()
        self.client.disconnect()
        self.setGuiConnected(False)
        self.window.listWidgetContacts.clear()

    def load_contacts(self, contacts):
        """получение списка контактов"""
        # Чистим список
        self.window.listWidgetContacts.clear()
        # Добавим
        for contact in contacts:
            self.window.listWidgetContacts.addItem(str(contact))

    def add_contact(self):
        """Добавление контакта"""
        # Получаем имя из QTextEdit
        try:
            username = self.window.textEditUsername.toPlainText()
            if username:
                # Соединение
                #client.connect()
                self.client.add_contact(username)
                self.window.listWidgetContacts.addItem(username)
                self.window.textEditUsername.clear()
                # отключаемся
                #client.disconnect()
        except Exception as e:
            print("Ошибка в функции add_contact:", e)

    def del_contact(self):
        try:
            current_item = self.window.listWidgetContacts.currentItem()
            username = current_item.text()
            # Соединение
            #client.connect()
            self.client.del_contact(username)
            # отключаемся
            #client.disconnect()
            current_item = self.window.listWidgetContacts.takeItem(self.window.listWidgetContacts.row(current_item))
            del current_item
        except Exception as e:
            print("Ошибка в функции del_contact:", e)

    def send_message(self):
        text = self.window.textEditMessage.toPlainText()
        if text:
            try:
                selected_index = self.window.listWidgetContacts.currentIndex()
                if selected_index:
                    user_name = selected_index.data()
                    # Соединение
                    #client.connect()
                    for dict_public_key in self.client.user_public_keys:
                        # При отправки сообщение сначала отправляем один раз одному из клиентов Публичный ключ
                        if dict_public_key["name"] == user_name and dict_public_key["is_send_public_key"] == False:
                            dict_public_key["is_send_public_key"] = True
                            self.client.send_crypto(user_name, self.client.user_pub.n)
                            self.window.listWidgetMessages.addItem("Публичный ключ от пользователя {} еще не получен, "
                                                                   "но наш публичный ключ отправлен попробуйте еще раз".format(
                                user_name))
                            # Еще бы неплохо получать ответ от пользователя что он получил ключ
                        # Если у нас сохранен публичный ключ клиента то шифруем им сообщение
                        if dict_public_key["name"] == user_name and dict_public_key["is_received_public_key"] == True \
                                and dict_public_key["public_key"] != None:
                            message = text.encode("utf-8")
                            public_key = rsa.PublicKey(dict_public_key["public_key"], 65537)
                            crypto = rsa.encrypt(message, public_key)
                            self.client.send_message(user_name, crypto.decode("ISO-8859-1"))
                    # отключаемся
                    #client.disconnect()
                    msg = ' {}: {}'.format(name, text)
                    self.window.listWidgetMessages.addItem(msg)
                self.window.textEditMessage.clear()
            except Exception as e:
                print("Ошибка в функции graphic_chat.send_message:", e)

    def setGuiConnected(self, enabled):
        ''' Настройка GUI при подключении/отключении
        '''
        self.window.listWidgetMessages.setEnabled(enabled)
        self.window.textEditMessage.setEnabled(enabled)
        self.window.pushButtonSend.setEnabled(enabled)
        self.window.clearTextButton.setEnabled(enabled)
        self.window.connectButton.setEnabled(not enabled)
        self.window.disconnectButton.setEnabled(enabled)
        self.window.listWidgetContacts.setEnabled(enabled)
        self.window.textEditUsername.setEnabled(enabled)
        self.window.textEditUsername.setEnabled(enabled)
        self.window.pushButtonAddContact.setEnabled(enabled)
        self.window.pushButtonDelContact.setEnabled(enabled)

    def clear_text(self):
        self.window.listWidgetMessages.clear()

    def start_chat(self):
        #name, password, result = AuthenticateDialog().get_username()

        # Создать контроллер
        self.client = User(self.name, self.password, addr, port)
        #print("Публичный ключ: {}, Приватный ключ: {} ".format(self.client.user_pub, self.client.user_priv))
        self.window.setWindowTitle("Мессенджер - {}".format(self.name))
        self.setGuiConnected(True)
        try:
            response = self.client.connect()
            if ERROR in response:
                if str(response[ERROR]) == str(WRONG_LOGIN):
                    self.show_error_msg('Неверный логин', QMessageBox.Critical)
                    self.client.disconnect()
                    self.setGuiConnected(False)
                    self.window.listWidgetContacts.clear()
                elif str(response[ERROR]) == str(WRONG_PASSWORD):
                    self.show_error_msg('Неверный пароль', QMessageBox.Critical)
                    self.client.disconnect()
                    self.setGuiConnected(False)
                    self.window.listWidgetContacts.clear()
            elif RESPONSE in response:
                if str(response[RESPONSE]) == str(OK):
                    self.receiver = GuiReceiver(self.client.sock, self.client.request_queue)
                    self.receiver.gotData.connect(self.update_chat)
                    self.receiver.gotCryptoData.connect(self.append_user_public_keys)
                    # Создание потока и помещение объекта-монитора в этот поток
                    self.thread = QThread()
                    self.receiver.moveToThread(self.thread)

                    # ---------- Важная часть - связывание сигналов и слотов ----------
                    # При запуске потока будет вызван метод search_text
                    self.thread.started.connect(self.receiver.poll)

                    # При завершении поиска необходимо завершить поток и изменить GUI
                    self.receiver.finished.connect(self.thread.quit)
                    self.receiver.finished.connect(self.finished)

                    # Запуск потока, который запустит self.monitor.search_text
                    self.thread.start()

                    self.contact_list, self.quantity = self.client.get_contacts()

                    if self.quantity < 0:
                        self.show_error_msg('У вас еще нет контактов!', QMessageBox.Warning)
                        return
                    for user_name in self.contact_list:
                        user_public_keys_dict = {"name": user_name, "is_send_public_key": False, "is_received_public_key": False, "public_key": None}
                        self.client.user_public_keys.append(user_public_keys_dict)

                    # грузим контакты в список сразу при запуске приложения
                    self.load_contacts(self.contact_list)
                else:
                    raise ConnectionRefusedError
        except ConnectionRefusedError as e:
            print('Сервер недоступен')
            self.show_error_msg('Сервер недоступен!', QMessageBox.Critical)
            sys.exit()
        except Exception as e:
            print("Ошибка в функции start_chat:", e)


    def show_error_msg(self, text, status):
        msg = QMessageBox()
        msg.setText(text)
        msg.setIcon(status)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


    @pyqtSlot(tuple)
    def update_chat(self, data):
        try:
            from_, message = data
            #print(from_, message.encode("ISO-8859-1"))
            message = rsa.decrypt(message.encode("ISO-8859-1"), self.client.user_priv)
            msg = '{}: >>> {}'.format(from_, message.decode("utf-8"))
            self.window.listWidgetMessages.addItem(msg)
        except rsa.DecryptionError as e:
            print(e)
        except Exception as e:
            print("Ошибка в функции update_chat:", e)


    @pyqtSlot(tuple)
    def append_user_public_keys(self, data):
        try:
            user_name, public_key = data
            for dict_public_key in self.client.user_public_keys:
                if dict_public_key["name"] == user_name and dict_public_key["is_received_public_key"] == False:
                    dict_public_key["public_key"] = public_key
                    dict_public_key["is_received_public_key"] = True
                    print('Получен первичный ключ от пользователя {} public_key: {}'.format(user_name, public_key))
                    self.window.listWidgetMessages.addItem(
                        'Получен первичный ключ от пользователя {} public_key: {}'.format(user_name, public_key))
                    if dict_public_key["name"] == user_name and dict_public_key["is_send_public_key"] == False:
                        # Отсылаем в ответ наш публичный ключ
                        self.client.send_crypto(user_name, self.client.user_pub.n)
                        dict_public_key["is_send_public_key"] = True



        except Exception as e:
            print("Ошибка в функции append_user_public_keys:", e)



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
    except IndexError:
        name = 'Leo'
    try:
        password = sys.argv[4]
    except IndexError:
        password = '12345'

    app = QtWidgets.QApplication(sys.argv)
    window = GraphicChat(name, password)
    sys.exit(app.exec_())

