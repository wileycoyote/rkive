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

class MoviesToMovieSet(Base):
    __tablename__ = 'moviestomovieset'
    movieid = Column(Integer, primary_key=True)
    movieboxsetid =Column(Integer)
    movies = relationship("Movie", ForeignKey("movie.id"))
    movieboxset = relationship("MovieSet", ForeignKey("movieset.id"))

class MovieSet(Base):
    __tablename__ = 'movieset'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    year = Column(Date)

class AlbumSchema(Base):
    __tablename__ = 'album'
    Column('title', String)
    id = Column(Integer, primary_key=True)
    Column('subtitle',String)
    Column('discnumber', String)
    Column('tracktotal', String)
    Column('index', String)

    def __init__(self, title=None, subtitle=None, discnumber=None, tracktotal=None, indx=None):
        self.title = title
        self.subtitle = subtitle
        self.discnumber = discnumber
        self.tracktotal = tracktotal
        self.indx = indx

class AlbumsToAlbumSet(Base):
    __tablename__ = 'albumstoalbumset'
    albumid = Column(Integer, primary_key=True)
    albums = relationship('Album', ForeignKey('album.id'))
    albumset = relationship('AlbumSet', ForeignKey('albumset.id'))

class AlbumSet(Base):
    __tablename__ = 'albumset'
    id = Column(Integer, primary_key=True)
    Column('disctotal', String)
    Column('discnumber', String)

class AlbumTracks(Base):
    __tablename__ = 'albumtracks'
    albumid = Column(Integer, primary_key=True)
    trackid = Column(Integer, primary_key=True)
    album = relationship('Album', ForeignKey('album.id'))
    track = relationship('Track', ForeignKey('MusicTrack.id'))

class MusicTrackSchema(Base):
    __tablename__ = 'musictrack'
    id = Column('id', Integer, primary_key=True)
    Column('mediaid', Integer)
    Column('title', String)
    Column('tracknumber', String)
    Column('genre', String, nullable=True)
    Column('composer', String, nullable=True)
    Column('comment', String, nullable=True)
    Column('hash', String, index=True)

    def __init__(self, path):
        log = getLogger('Rkive.Index')

