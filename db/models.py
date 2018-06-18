from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Numeric, String, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from db.config import *
from sqlalchemy.orm import relationship

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
Base = declarative_base()


class ContactList(Base):
    __tablename__ = 'contact_list'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    contact_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    client = relationship("User", backref="clients", primaryjoin="User.id==ContactList.client_id")
    contact = relationship("User", backref="contacts", primaryjoin="User.id==ContactList.contact_id")

    def __init__(self, client_id, contact_id):
        self.client_id = client_id
        self.contact_id = contact_id

    def __repr__(self):
        return "<User('%s','%s')>" % (self.client_id, self.contact_id)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String)
    information = Column(String)

    client = relationship("ContactList", backref="clients", primaryjoin="User.id==ContactList.client_id")
    contact = relationship("ContactList", backref="contacts", primaryjoin="User.id==ContactList.contact_id")

    def __init__(self, login, information):
        self.login = login
        self.information = information

    def __repr__(self):
        return "<User('%s','%s')>" % (self.login, self.information)


class CustomerHistory(Base):
    __tablename__ = 'customer_history'
    id = Column(Integer, primary_key=True)
    entry_time = Column(String)
    ip = Column(String)

    def __init__(self, entry_time, ip):
        self.entry_time = entry_time
        self.ip = ip

    def __repr__(self):
        return "<User('%s','%s')>" % (self.entry_time, self.ip)




# Создание таблицы
Base.metadata.create_all(engine)
