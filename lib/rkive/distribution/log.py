import os
import datetime
from logging import getLogger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine, DateTime, func
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Log(Base):
    __tablename__ = 'uploaded'
    id        = Column('id', Integer, primary_key=True)
    datetime  = Column('datetime', DateTime, server_default=func.now())
    local       = Column('local', String)
    remote       = Column('remote', String)
    server    = Column('server', String)
    ipaddress = Column('ipadress', String)
    size      = Column('size', Integer)

    def __init__(self, from_fp, to_fp, server, ipaddress, size):
        self.from_fp = from_fp
        self.to_fp = to_fp
        self.server = server
        self.ipaddress = ipaddress
        self.size = size

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
db = 'sqlite:///'+os.environ['HOME']+'/Uploads/uploads.db'
engine = create_engine(db)
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Log.metadata.create_all(engine)
Log.metadata.bind = engine
DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

