import os
import datetime
from logging import getLogger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine, DateTime, func, ForeignKey
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Sender(Base):
    __tablename__ = 'sender'
    name = Column('name', String)
    ipaddress = Column('ipaddress', String)
    base = Column('base', String) 
    relative_key = Column('relative_key', String, primary_key=True)

    def __init__(self,  ipaddress, base, relative_key, server='localhost'):
        self.ipaddress = ipaddress
        self.name = server
        self.base = base
        self.relative_key = relative_key


class Receiver(Base):
    __tablename__='receiver'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)
    ipaddress = Column('ipaddress', String)
    base = Column('base', String)
    relative_key = Column('relative_key', String, ForeignKey("sender.relative_key"), nullable=False)

    def __init__(self, ipaddress, base, relative_key, server='localhost'):
        self.ipaddress = ipaddress
        self.name = server
        self.base = base
        self.relative_key = relative_key

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
# postgresql://scott:tiger@localhost:5432/mydatabase
db = 'postgresql://admin:admin@192.168.1.172/distribution'
print "ENGINE: "+db 
engine = create_engine(db)
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Receiver.metadata.create_all(engine)
Receiver.metadata.bind = engine
Sender.metadata.create_all(engine)
Sender.metadata.bind = engine
DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

