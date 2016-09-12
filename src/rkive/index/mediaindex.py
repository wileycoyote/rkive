#!/usr/bin/env python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from rkive.index.musicfile import MusicFile

Base = declarative_base()

class MusicTrack(Base, MusicFile):
    __tablename__ = 'MusicTrack'
    id_track = Column('idMusicTrack', Integer, primary_key=True)
    Column('discnumber', String)
    Column('disctotal', String)
    Column('album', String)
    Column('title', String)
    Column('filepath', String)
    Column('tracktotal', String)
    Column('tracknumber', String)
    Column('artist', String, nullable=True)
    Column('albumartist', String, nullable=True)
    Column('genre', String, nullable=True)
    Column('composer', String, nullable=True)
    Column('comment', String, nullable=True)

    def __init__(self, path):
        MusicFile.__init__(path)

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
