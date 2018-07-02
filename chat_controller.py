from PyQt5.QtCore import QObject, pyqtSignal
from jim.core import Jim, JimMessage
from jim.utils import get_message


class Receiver:
    def __init__(self, sock, request_queue):
        self.request_queue = request_queue
        self.sock = sock
        self.is_alive = False

    def process_message(self, message):
        pass

    def poll(self):
        self.is_alive = True
        while True:
            if not self.is_alive:
                break
            else:
                data = get_message(self.sock)
                print("Testing:", data)
            try:
                if isinstance(data, dict):
                    jm = Jim.from_dict(data)
                    if isinstance(jm, JimMessage):
                        self.process_message(jm)
                    else:
                        self.request_queue.put(jm)
            except Exception as e:
                print(e)

    def stop(self):
        self.is_alive = False


class ConsoleReceiver(Receiver):
    def process_message(self, message):
        print('\n>> {}: {}'.format(message.from_, message.message))


class GuiReceiver(Receiver, QObject):
    gotData = pyqtSignal(str)
    finished = pyqtSignal(int)


    def __init__(self, sock, request_queue):
        Receiver.__init__(self, sock, request_queue)
        QObject.__init__(self)

    def process_message(self, message):
        text='{}: {}'.format(message.from_, message.message)
        self.gotData.emit(text)

    def poll(self):
        super().poll()
        self.finished.emit(0)

    def stop(self):
        super().stop()