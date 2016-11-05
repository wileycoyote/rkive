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

class Movies(object):

    film_re = re.compile('(.+?) \((.*?), (\d\d\d\d)\)')

    def __init__(self, session):
        self.session = session

    def parse_midx(self, midx):
        m = self.film_re.match(midx)
        return(m.group(1),m.group(2),m.group(3))

    def add_movie(self, title, directors, year, fp):
        log = getLogger('Rkive.Index')
        log.info("title: {0}".format(title))
        people=[]
        directors = directors.split(', ')
        for d in directors:
            log.info("title: {0}".format(d))
            p = Person(d)
            log.info("title: {0}".format(d))
            self.session.add(p)
            mp = Moviepeople('director', p)
            self.session.add(mp)
            self.session.commit()
            people.append(mp)
        t ='mkv'
        media = Media(t, fp)
        self.session.add(media)
        self.session.commit()
        movie = Movie(title, year)
        log.info("add_person: {0}".format(people))
        movie.add_person(people)
        log.info("title: {0}".format(d))
        movie.add_media(media)
        log.info("title: {0}".format(d))
        self.session.add(movie)
        self.session.commit()

    def get_movies(self):
        return self.session.query(Movie.title).all()
    #
    # returns a list of <movie_name> (<director(s)>, <year>)
    def get_movies_index(self):
        log = getLogger('Rkive.Index')
        movie_info = set()
        movies = self.session.query(Movie).all()
        for movie in movies:
            info = rkive.index.schema.Movie.get_movie_index(movie)
            movie_info.add(info)
        return movie_info

    def get_movie_index(movie):
        directors = []
        for p in movie.people:
            if p.role=='director':
                directors.append(p.name)
        year =''
        for m in movie.mediaobjects:
            if m.media_format == 'mkv':
                year = m.year_released
        directors = ', '.join(directors)
        return '{0} ({1}, {2})'.format(movie.title, directors, year)

    def find_movie(self, title, fmt, year,directors=[] ):
        role='director'
        movie = None
        try:
            movie=self.session.query(Movie, Media).\
            filter_by(title=title).\
            filter(Media.format==fmt,Movie.year==year,Movie.id==Media.id).\
            filter(and_(Movie.people.any(People.role==role), People.name.in_(directors))).\
            one()
        except alchemy_exceptions.SQLAlchemyError:
            return movie
        return movie

    @classmethod
    def is_movie(cls, root, name):
        log = getLogger('Rkive.Index')
        m = cls.film_re.match(name)
        log.debug("Found: {0} {1}".format(m, name))
        if not m:
            return False
        return True

    def remove_movies(movies):
        for movie in movies:
            m = Movies.film_re.match(movie)
            title = m.group(1)
            directors = m.group(2).split(', ')
            year = m.group(3)
            movie_in_db = Movie.find_movie(title, 'mkv', year, directors)
            movie_in_db.delete(synchronize_session=True)

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
        attr=MusicFile.__init__(path)
        for a in attr:
            print( attr[a])

