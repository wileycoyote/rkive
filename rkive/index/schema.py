from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Table, Date
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
    movie = relationship('Movie')

    def __init__(self, r, p, m):
        self.role = r
        self.person = p
        self.movie = m

class Moviemedia(Base):
    __tablename__ = 'moviemedia'

class Movie(Base):
    __tablename__ = 'movie'
    Column('workid', Integer, primary_key=True)
    title = Column(String)
    category = Column(String)
    year = Column(String)
    mediaobjects = relationship("Moviemedia", backref='movie', cascade="all, delete, delete-orphan")
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

class Musicmedia(Base):
    __tablename__ = 'musicmedia'
    id = Column(Integer, primary_key=True)
    media_id = Column(Integer, ForeignKey('media.id'))
    file = relationship("File")
    musictrack_id = Column(Integer, ForeignKey("musictrack.id"))
    musictrack = relationship('Musictrack')

    def __init__(self, m, f):
        self.musictrack = m
        self.file = f

class Musictrack(Base):
    __tablename__ = 'musictrack'
    people = relationship("Musicpeople", backref='musictrack', cascade="all, delete, delete-orphan")
    mediaobjects = relationship("Musicmedia", backref='musictrack', cascade="all, delete, delete-orphan")
    id = Column('id', Integer, primary_key=True)
    Column('albumname', String, primary_key=True)
    Column('series_number', Integer, primary_key=True)
    Column('tracknumber', Integer, primary_key=True)
    column('attrname', String)
    Column('attrval', String)

    def __init__(self, path):
        log = getLogger('Rkive.Index')

