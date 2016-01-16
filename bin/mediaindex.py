#!/usr/bin/env python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine

Base = declarative_base()
     
class MusicCollection(Base):
    __tablename__ = 'MusicCollection'
    idMusicCollection = Column('idMusicCollection', Integer, primary_key=True)
    Column('Name', String)
    Column('Folder', String)
    
class MusicTrack(Base):
    __tablename__ = 'MusicTrack'
    id_track = Column('idMusicTrack', Integer, primary_key=True)
    Column('CD', Integer)   
    Column(Integer, ForeignKey('MusicCollection.idMusicCollection',  onupdate="CASCADE", ondelete="CASCADE"))
    Column('Name', String)
    Column('Filename', String)
    Column('FullFilepath', String)
    Column('Artist', String, nullable=True)
    Column('Genre', String, nullable=True)
    Column('Composer', String, nullable=True)

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('postgresql://postgres:postgres@192.168.1.155/MediaIndex')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker()
DBSession.bind = engine
db = DBSession()
