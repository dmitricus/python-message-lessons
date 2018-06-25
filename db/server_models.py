import datetime
import os
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class ClientContact(Base):
    """Связка контакт-клиент для хранения списка контактов"""
    # Название таблицы
    __tablename__ = 'ClientContact'
    # Первичный ключ
    ClientContactId = Column(Integer, primary_key=True)
    # id клиента
    ClientId = Column(Integer, ForeignKey('Client.ClientId'))
    # id контакта клиента
    ContactId = Column(Integer, ForeignKey('Client.ClientId'))

    client = relationship("Client", backref="clients", primaryjoin="Client.ClientId==ClientContact.ClientId")
    contact = relationship("Client", backref="contacts", primaryjoin="Client.ClientId==ClientContact.ContactId")

    def __init__(self, client_id, contact_id):
        self.ClientId = client_id
        self.ContactId = contact_id


class Client(Base):
    """Клиент"""
    # Название таблицы
    __tablename__ = 'Client'
    # Первичный ключ
    ClientId = Column(Integer, primary_key=True)
    # Имя клиента
    Name = Column(String, unique=True)
    # Информация не обязательное поле
    Info = Column(String, nullable=True)

    client = relationship("ClientContact", backref="clients", primaryjoin="Client.ClientId==ClientContact.ClientId")
    contact = relationship("ClientContact", backref="contacts", primaryjoin="Client.ClientId==ClientContact.ContactId")


    def __init__(self, name, info=None):
        self.Name = name
        if info:
            self.Info = info

    def __repr__(self):
        return "<Client ('%s')>" % self.Name

    def __eq__(self, other):
        # Клиенты равны если равны их имена
        return self.Name == other.Name

class CustomerHistory(Base):
    __tablename__ = 'CustomerHistory'
    id = Column(Integer, primary_key=True)
    entry_time = Column(String)
    ip = Column(String)

    def __init__(self, entry_time, ip):
        self.entry_time = entry_time
        self.ip = ip


# путь до папки где лежит этот модуль
DB_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
# путь до файла базы данных
DB_PATH = os.path.join(DB_FOLDER_PATH, 'server.db')
#создаем движок
engine = create_engine('sqlite:///{}'.format(DB_PATH), echo=False)
# Не забываем создать структуру базы данных
Base.metadata.create_all(engine)
# Создаем сессию для работы
Session = sessionmaker(bind=engine)
session = Session()
# Рекомендуется брать 1 сессию и передавать параметром куда нам надо
# session = session
