from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Table
import sqlalchemy.exc as alchemy_exceptions
from sqlalchemy import create_engine, or_, and_
import re

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
    id = Column(Integer, primary_key=True),
    name = Column(String)

    def __init__(self, n):
        self.name = n

class MoviePeople(Base):
    __tablename__ = 'moviepeople'
    id = Column(Integer, primary_key=True)
    role = Column(String)
    people_id = Column(Integer, ForeignKey('people.id'))
    person = relationship("Person")
    movie_id = Column(Integer, ForeignKey("movie.id"))

    def __init__(self, r, p):
        self.role = r
        self.person = p

class Movie(Base):
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    category = Column(String)
    year = Column(String)
    mediaobjects = relationship("Media", cascade="all, delete, delete-orphan")
    people = relationship("MoviePeople", cascade="all, delete, delete-orphan")

    def __init__(self, title, year, fp):
        self.title = title
        self.director = []
        self.year = year
        self.category = 'movie'

    def p(self):
        directors = ', '.join(self.directors)
        p='{0} ({1}, {2})'.format(self.title, directors, self.year)
        print(p)

    def add_media(self, m):
        self.mediaobjects.append(m)

    def add_person(self, person):
        self.people.append(person)

class Movies(Base):

    session = None
    file_re = re.compile('(.+?) \((.*?)\), \((\d\d\d\d)\)')

    def add_movie(title, year, directors, fp):
        m = Movie(title, year)
        for d in directors:
            p = Person(d)
            session.add(p)
            mp = MoviePeople('director', p)
            session.add(mp)
            m.add_person(mp)
        t ='mkv'
        media = MediaObject(t, fp)
        session.add(media)
        m.add_media(media)
        session.add(m)
        session.commit()

    def get_movies():
        return Movies.session.query(Movie.title).all()
    #
    # returns a list of <movie_name> (<director(s)>, <year>)
    def get_movies_index():
        movie_info = set()
        movies = Movies.session.query(Movie).all()
        for movie in movies:
            info = Movie.get_movie_index(movie)
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

    def find_movie(title, fmt, year,directors=[] ):
        role='director'
        movie = None
        try:
            movie=Movies.session.query(Movie, Media).\
            filter_by(title=title).\
            filter(Media.format==fmt,Movie.year==year,Movie.id==Media.id).\
            filter(and_(Movie.people.any(People.role==role), People.name.in_(directors))).\
            one()
        except alchemy_exceptions.SQLAlchemyError:
            return movie
        return movie

    def is_movie(s):
        m = self.film_re.match(s)
        if not m:
            return False
        movie = m.group(1)
        director = m.group(2)
        year = m.group(3)
        directors = director.split(', ')
        if Movies.find_movie(movie, 'mkv', year, directors):
            return True
        m = self.add_movie(movie, directors, year)
        m.save()
        return True

    def remove_movies(movies):
        for movie in movies:
            m = Movies.film_re.match(movie)
            title = m.group(1)
            directors = m.group(2).split(', ')
            year = m.group(3)
            movie_in_db = Movie.find_movie(title, 'mkv', year, directors)
            movie_in_db.delete(synchronize_session=True)
