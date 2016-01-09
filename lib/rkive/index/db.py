#/usr/bin/env python
import logging
from logging import getLogger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine

Base = declarative_base()
     
class MusicAlbum(Base):
    __tablename__ = 'MusicAlbum'
    idMusicAlbum = Column('idMusicAlbum', Integer)
    
class MusicTrack(Base):
    __tablename__ = 'MusicTrack'
    idMusicTrack = Column('idMusicTrack', Integer)
    idMusicAlbum = Column(Integer, ForeignKey('MusicAlbum.idMusicAlbum',  onupdate="CASCADE", ondelete="CASCADE"))

class MusicAttr(Base):
    __tablename__ = 'MusicTag'
    idMusicTrack = Column(String, ForeignKey('MusicTrack.idMusicTrack',  onupdate="CASCADE", ondelete="CASCADE"))
    idMusicAttr = Column('idMusicAttr', Integer)
    name = Column('name', String)
    value = Column('value', String)
    category = Column('category', String)

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('postgresql://postgres:postgres@192.168.2.6/magpie')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker()
DBSession.bind = engine
db = DBSession()
