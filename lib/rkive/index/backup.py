#!/usr/bin/env python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine

Base = declarative_base()
     
class FilePath(Base):
    __tablename__ = ''
    id_track = Column('id', Integer, primary_key=True)
    Column('filepath', String)   
    Column('modtime', String)
        
# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('postgresql://postgres:postgres@192.168.1.155/BackupIndex')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker()
DBSession.bind = engine
db = DBSession()
