import sys
from PyQt5.QtCore import QMetaObject, QRect, QCoreApplication
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, QLabel, QApplication


class AuthenticateDialog(QDialog):
    def __init__(self, parent=None):
        #super(AuthenticateDialog, self).__init__(parent)
        QDialog.__init__(self, parent)
        self.setWindowTitle('Введите имя пользователя')
        self.setupUi(self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(261, 134)
        self.username_edit = QLineEdit(Dialog)
        self.username_edit.setGeometry(QRect(70, 20, 171, 20))
        self.username_edit.setObjectName("username_edit")
        self.password_edit = QLineEdit(Dialog)
        self.password_edit.setGeometry(QRect(70, 60, 171, 20))
        self.password_edit.setObjectName("password_edit")
        self.username_label = QLabel(Dialog)
        self.username_label.setGeometry(QRect(10, 20, 47, 13))
        self.username_label.setObjectName("username_label")
        self.password_label = QLabel(Dialog)
        self.password_label.setGeometry(QRect(10, 60, 47, 13))
        self.password_label.setObjectName("password_label")
        self.buttons = QDialogButtonBox(Dialog)
        self.buttons.setGeometry(QRect(130, 90, 111, 41))
        self.buttons.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttons.setObjectName("buttons")
        self.retranslateUi(Dialog)
        QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Авторизация"))
        self.username_label.setText(_translate("Dialog", "Логин:"))
        self.password_label.setText(_translate("Dialog", "Пароль:"))

    # Получить имя из диалога
    def username(self):
        return self.username_edit.text(), self.password_edit.text()

    # Создать диалог и вернуть юзернейм
    @staticmethod
    def get_username(parent=None):
        dialog = AuthenticateDialog(parent)
        result = dialog.exec_()
        name, password = dialog.username()
        return name, password, result == QDialog.Accepted

if __name__ == '__main__':
    app = QApplication(sys.argv)
    name, password, result = AuthenticateDialog().get_username()
    print(name, password, result)
    sys.exit(app.exec_())