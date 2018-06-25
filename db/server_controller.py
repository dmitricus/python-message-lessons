from .server_models import Client, ClientContact, CustomerHistory
from .server_errors import ContactDoesNotExist
from sqlalchemy.exc import SQLAlchemyError

class Storage:
    """Серверное хранилище"""

    def __init__(self, session):
        """
        Запоминаем сессию, чтобы было удобно с ней работать
        :param session:
        """
        self.session = session

    def add_client(self, username, info=None):
        """Добавление клиента"""
        new_item = Client(username, info)
        self.session.add(new_item)
        self.session.commit()

    def client_exists(self, username):
        """Проверка, что клиент уже есть"""
        result = self.session.query(Client).filter(Client.Name == username).count() > 0
        return result

    def get_client_by_username(self, username):
        """Получение клиента по имени"""
        client = self.session.query(Client).filter(Client.Name == username).first()
        return client

    def add_contact(self, client_username, contact_username):
        """Добавление контакта"""
        contact = self.get_client_by_username(contact_username)
        if contact:
            client = self.get_client_by_username(client_username)
            if client:
                cc = ClientContact(client_id=client.ClientId, contact_id=contact.ClientId)
                self.session.add(cc)
                self.session.commit()
            else:
                # raise NoneClientError(client_username)
                pass
        else:
            raise ContactDoesNotExist(contact_username)

    def del_contact(self, client_username, contact_username):
        """Удаление контакта"""
        contact = self.get_client_by_username(contact_username)
        if contact:
            client = self.get_client_by_username(client_username)
            if client:
                cc = self.session.query(ClientContact).filter(
                    ClientContact.ClientId == client.ClientId).filter(
                    ClientContact.ContactId == contact.ClientId).first()
                self.session.delete(cc)
            else:
                # raise NoneClientError(client_username)
                pass
        else:
            raise ContactDoesNotExist(contact_username)

    def get_contacts(self, client_username):
        """Получение контактов клиента"""
        client = self.get_client_by_username(client_username)
        result = []
        if client:
            # Тут нету relationship поэтому берем запросом
            contacts_clients = self.session.query(ClientContact).filter(ClientContact.ClientId == client.ClientId)
            for contact_client in contacts_clients:
                contact = self.session.query(Client).filter(Client.ClientId == contact_client.ContactId).first()
                result.append(contact)
        return result

    def get_clients(self):
        """Получение списка клиентов"""
        clients = self.session.query(Client).all()
        return clients

    def get_histories(self):
        """Получение истории подключений"""
        histories = self.session.query(CustomerHistory).all()
        return histories

    ########## SELECT #########################
    def select_users(self, login=None):
        try:
            if login:
                # Выборка по логину
                q_user = self.session.query(Client).filter_by(login=login).first()
                return q_user.login, q_user.information
            else:
                # Все пользователи
                q_user = self.session.query(Client).all()
                return q_user
        except SQLAlchemyError as ex:
            print("Ошибка: {0}".format(ex))
        finally:
            self.session.close()

    def select_customer_history(self, ip=None):
        try:
            if ip:
                # Выборка
                q_customer_history = self.session.query(CustomerHistory).filter_by(ip=ip).first()
                return q_customer_history.entry_time, q_customer_history.ip
            else:
                # Все
                q_customer_history = self.session.query(CustomerHistory).all()
                return q_customer_history
        except SQLAlchemyError as ex:
            print("Ошибка: {0}".format(ex))
        finally:
            self.session.close()

    def select_contact_list(self, login=None):
        try:
            if login:
                # Получим id пользователя
                q_user = self.session.query(Client.id).filter(Client.login == "Dmitricus")
                # Получим список контактов пользователя
                q_contact_list = self.session.query(ClientContact.contact_id).filter(ClientContact.client_id.in_(q_user))
                # Посчитаем сколько сонтактов в списке
                q_contact_list_count = self.session.query(ClientContact.contact_id) \
                    .filter(ClientContact.client_id.in_(q_user)).count()
                # Выведем список логинов пользователей
                q_contact_user = self.session.query(Client.login).filter(Client.id.in_(q_contact_list)).all()
                return q_contact_user, q_contact_list_count
            else:
                # Все
                q_contact_list = self.session.query(ClientContact).all()
                return q_contact_list
        except SQLAlchemyError as ex:
            print("Ошибка: {0}".format(ex))
        finally:
            self.session.close()

    ###########################################

    ########## INSERT #########################
    def insert_users(self, login, information):
        try:
            # Для сохранения объекта User, нужно добавить его к имеющейся сессии
            client = Client(login, information)
            self.session.add(client)
        except SQLAlchemyError as ex:
            print("Ошибка: {0}".format(ex))
            self.session.rollback()
        else:
            self.session.commit()
        finally:
            self.session.close()

    def insert_contact_list(self, login):
        try:
            # Для сохранения объекта User, нужно добавить его к имеющейся сессии
            client = Client(login)
            self.session.add(client)
        except SQLAlchemyError as ex:
            print("Ошибка: {0}".format(ex))
            self.session.rollback()
        else:
            self.session.commit()
        finally:
            self.session.close()

    ###########################################

    ########## DELETE #########################
    def delete_users(self, login, information):
        try:
            client = Client(login, information)
            # Для сохранения объекта User, нужно добавить его к имеющейся сессии
            self.session.delete(client)
        except SQLAlchemyError as ex:
            print("Ошибка: {0}".format(ex))
            self.session.rollback()
        else:
            self.session.commit()
        finally:
            self.session.close()

    def delete_contact_list(self, login):
        try:
            client = Client(login)
            # Для сохранения объекта User, нужно добавить его к имеющейся сессии
            self.session.delete(Client)
        except SQLAlchemyError as ex:
            print("Ошибка: {0}".format(ex))
            self.session.rollback()
        else:
            self.session.commit()
        finally:
            self.session.close()
    ###########################################