#/usr/bin/env python
import logging
from logging import getLogger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine

Base = declarative_base()
     
class MusicCollection(Base):
    __tablename__ = 'MusicCollection'
    idMusicAlbum = Column('idMusicCollection', Integer)
    Column('Name', String)
    Column('Folder', String)
    
class MusicTrack(Base):
    __tablename__ = 'MusicTrack'
    idMusicTrack = Column('idMusicTrack', Integer)
    cd = Column('CD', Integer)   
    idMusicAlbum = Column(Integer, ForeignKey('MusicCollection.idMusicCollection',  onupdate="CASCADE", ondelete="CASCADE"))
    Column('Name', String)
    column('Filename', String)
    column('FullFilepath', String)

class MusicArtist(Base):
    __tablename__ = 'MusicTag'
    idMusicArtist = Column(String, ForeignKey('MusicTrack.idMusicTrack',  onupdate="CASCADE", ondelete="CASCADE"))
    name = Column('name', String)

class MusicGenre(Base):
    __tablename__ = 'MusicTag'
    idMusicArtist = Column(String, ForeignKey('MusicTrack.idMusicTrack',  onupdate="CASCADE", ondelete="CASCADE"))
    idMusicAttr = Column('idMusicAttr', Integer)
    name = Column('name', String)

class Composer(Base):
    idMusicArtist = Column(String, ForeignKey('MusicTrack.idMusicTrack',  onupdate="CASCADE", ondelete="CASCADE"))
    __tablename__ = 'Composer'
    Column('Name', String)


# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('postgresql://postgres:postgres@192.168.1.155/index')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker()
DBSession.bind = engine
db = DBSession()
