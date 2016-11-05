from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Table
import sqlalchemy.exc as alchemy_exceptions
from sqlalchemy import create_engine, or_, and_
import re
from rkive.index.musicfile import MusicFile as MusicFile
from logging import getLogger

Base = declarative_base()

class Media(Base):
    __tablename__='media'
    id = Column(Integer, primary_key=True)
    filepath = Column(String)
    format = Column(String)
    movie_id = Column(Integer, ForeignKey("movie.id"))

    def __init__(self, fp, fmt):
        self.filepath = fp
        self.format = fmt

class Person(Base):
    __tablename__='person'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, n):
        self.name = n

class Moviepeople(Base):
    __tablename__ = 'moviepeople'
    id = Column(Integer, primary_key=True)
    role = Column(String)
    people_id = Column(Integer, ForeignKey('person.id'))
    person = relationship("Person")
    movie_id = Column(Integer, ForeignKey("movie.id"))

    def __init__(self, r, p):
        self.role = r
        self.person = p

class Musicpeople(Base):
    __tablename__ = 'musicpeople'
    id = Column(Integer, primary_key=True)
    role = Column(String)
    people_id = Column(Integer, ForeignKey('person.id'))
    person = relationship("Person")
    musictrack_id = Column(Integer, ForeignKey("musictrack.id"))

    def __init__(self, r, p):
        self.role = r
        self.person = p

class Movie(Base):
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    category = Column(String)
    year = Column(String)
    mediaobjects = relationship("Media", backref='movie', cascade="all, delete, delete-orphan")
    people = relationship("Moviepeople", backref='movie', cascade="all, delete, delete-orphan")

    def __init__(self, title, year):
        self.title = title
        self.year = year
        self.category = 'movie'

    def p(self):
        directors = ', '.join(self.directors)
        p='{0} ({1}, {2})'.format(self.title, directors, self.year)
        print(p)

    def add_media(self, m):
        self.mediaobjects.append(m)

    def add_person(self, people):
        for person in people:
            self.people.append(person)

class Album(Base):
    pass

class AlbumSet(Base):
    pass

class MusicTrack(Base):
    __tablename__ = 'musictrack'
    id = Column('id', Integer, primary_key=True)
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
        log = getLogger('Rkive.Index')

