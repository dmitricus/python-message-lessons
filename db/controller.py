import sys
from db.models import User, CustomerHistory, ContactList, engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

Session = sessionmaker(bind=engine)

# Класс Хранилище - базовый класс, обеспечивающий сохранение данных
# (сохранение информации о пользователях на сервере, сохранение сообщений на стороне клиента).
class Storage:

    def __init__(self, user, customer_history, contact_list):
        """
            :param handler: обработчик событий
        """
        self.user = user
        self.customer_history = customer_history
        self.contact_list = contact_list

    ########## SELECT #########################
    def select_users(self, login=None):
        session = Session()
        try:
            if login:
                # Выборка по логину
                q_user = session.query(self.user).filter_by(login=login).first()
                return q_user.login, q_user.information
            else:
                # Все пользователи
                q_user = session.query(self.user).all()
                return q_user
        except SQLAlchemyError as ex:
            print("Ошибка: {0}".format(ex))
        finally:
            session.close()


    def select_customer_history(self, ip=None):
        session = Session()
        try:
            if ip:
                # Выборка
                q_customer_history = session.query(self.customer_history).filter_by(ip=ip).first()
                return q_customer_history.entry_time, q_customer_history.ip
            else:
                # Все
                q_customer_history = session.query(self.customer_history).all()
                return q_customer_history
        except SQLAlchemyError as ex:
            print("Ошибка: {0}".format(ex))
        finally:
            session.close()


    def select_contact_list(self, login=None):
        session = Session()
        try:
            if login:
                # Получим id пользователя
                q_user = session.query(User.id).filter(User.login == "Dmitricus")
                # Получим список контактов пользователя
                q_contact_list = session.query(ContactList.contact_id).filter(ContactList.client_id.in_(q_user))
                # Посчитаем сколько сонтактов в списке
                q_contact_list_count = session.query(ContactList.contact_id)\
                    .filter(ContactList.client_id.in_(q_user)).count()
                # Выведем список логинов пользователей
                q_contact_user = session.query(User.login).filter(User.id.in_(q_contact_list)).all()
                return q_contact_user, q_contact_list_count
            else:
                # Все
                q_contact_list = session.query(self.contact_list).all()
                return q_contact_list
        except SQLAlchemyError as ex:
            print("Ошибка: {0}".format(ex))
        finally:
            session.close()
    ###########################################

    ########## INSERT #########################
    def insert_users(self, login, information):
        session = Session()
        try:
            # Для сохранения объекта User, нужно добавить его к имеющейся сессии
            user = User(login, information)
            session.add(user)
        except SQLAlchemyError as ex:
            print("Ошибка: {0}".format(ex))
            session.rollback()
        else:
            session.commit()
        finally:
            session.close()

    def insert_contact_list(self, login):
        session = Session()
        try:
            # Для сохранения объекта User, нужно добавить его к имеющейся сессии
            user = User(login)
            session.add(user)
        except SQLAlchemyError as ex:
            print("Ошибка: {0}".format(ex))
            session.rollback()
        else:
            session.commit()
        finally:
            session.close()

    ###########################################

    ########## DELETE #########################
    def delete_users(self, login, information):
        session = Session()
        try:
            user = User(login, information)
            # Для сохранения объекта User, нужно добавить его к имеющейся сессии
            session.delete(user)
        except SQLAlchemyError as ex:
            print("Ошибка: {0}".format(ex))
            session.rollback()
        else:
            session.commit()
        finally:
            session.close()

    def delete_contact_list(self, login):
        session = Session()
        try:
            user = User(login)
            # Для сохранения объекта User, нужно добавить его к имеющейся сессии
            session.delete(user)
        except SQLAlchemyError as ex:
            print("Ошибка: {0}".format(ex))
            session.rollback()
        else:
            session.commit()
        finally:
            session.close()
    ###########################################


if __name__ == '__main__':
    user = User
    customer_history = CustomerHistory
    contact_list = ContactList
    storage = Storage(user, customer_history, contact_list)


    session = Session()
    # Получим id пользователя
    q_user = session.query(User.id).filter(User.login == "Dmitricus")
    # Получим список контактов пользователя
    q_contact_list = session.query(ContactList.contact_id).filter(ContactList.client_id.in_(q_user))
    # Посчитаем сколько сонтактов в списке
    q_contact_list_count = session.query(ContactList.contact_id).filter(ContactList.client_id.in_(q_user)).count()
    # Выведем список логинов пользователей
    q_contact_user = session.query(User.login).filter(User.id.in_(q_contact_list)).all()

    #print("Данные {} Тип данных {}".format(q_user, type(q_user)))
    #print("Данные {} Тип данных {}".format(q_contact_list, type(q_contact_list)))
    #print("Данные {} Тип данных {}".format(q_contact_list_count, type(q_contact_list_count)))
    print("Данные {} Тип данных {}".format(q_contact_user, type(q_contact_user)))
