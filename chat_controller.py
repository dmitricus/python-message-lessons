from PyQt5.QtCore import QObject, pyqtSignal
from jim.core import Jim, JimMessage, JimMessageCrypto
from jim.utils import get_message


class Receiver:
    def __init__(self, sock, request_queue):
        self.request_queue = request_queue
        self.sock = sock
        self.is_alive = False

    def process_message(self, message):
        pass

    def process_crypto(self, message):
        pass

    def poll(self):
        self.is_alive = True
        while True:
            if not self.is_alive:
                break
            data = get_message(self.sock)
            #print("Пришли данные: ", data)
            try:
                jm = Jim.from_dict(data)
                if isinstance(jm, JimMessage):
                    self.process_message(jm)
                if isinstance(jm, JimMessageCrypto):
                    self.process_crypto(jm)
                else:
                    self.request_queue.put(jm)
            except TypeError as e:
                print("Ошибка TypeError в функции Receiver.poll:", e)
            except Exception as e:
                print("Ошибка в функции Receiver.poll:", e)

    def stop(self):
        self.is_alive = False


class ConsoleReceiver(Receiver):
    def process_message(self, message):
        print('\n>> user {}: {}'.format(message.from_, message.message))


class GuiReceiver(Receiver, QObject):
    gotData = pyqtSignal(tuple)
    gotCryptoData = pyqtSignal(tuple)
    finished = pyqtSignal(int)


    def __init__(self, sock, request_queue):
        Receiver.__init__(self, sock, request_queue)
        QObject.__init__(self)

    def process_message(self, message):
        text = message.from_, message.message
        self.gotData.emit(text)

    def process_crypto(self, message):
        text = message.from_, message.public_key
        self.gotCryptoData.emit(text)

    def poll(self):
        super().poll()
        self.finished.emit(0)