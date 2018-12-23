from logging import getLogger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import and_
from sqlalchemy import Column, Integer, String


class Person(object):
    pass


class Movies(object):

    film_re = r'(.+?) \((.*?), (\d\d\d\d)\)'

    def __init__(self, session):
        self.session = session

    def parse_midx(self, midx):
        m = self.film_re.match(midx)
        return(m.group(1), m.group(2), m.group(3))

    def add_movie(self, title, year, fp):
        log = getLogger('Rkive.Index')
        log.info("title: {0}".format(title))
        t = 'mkv'
        log.info("add related info")
        media = Media(t, fp)
        self.session.add(media)
        self.session.commit()
        movie = Movie(title, year)
        movie.add_media(media)
        self.session.add(movie)
        self.session.commit()

    def get_movies(self):
        return self.session.query(Movie.title).all()

    # returns a list of <movie_name> (<director(s)>, <year>)
    def get_movies_index(self):
        log = getLogger('Rkive.Index')
        movie_info = set()
        movies = self.session.query(Movie).all()
        for movie in movies:
            log.debug(movie)
            info = self.get_movie_index(movie)
            movie_info.add(info)
        return movie_info

    def get_movie_index(self, movie):
        directors = []
        for p in movie.people:
            if p.role == 'director':
                directors.append(p.name)
        year = ''
        for m in movie.media:
            if m.media_format == 'mkv':
                year = m.year_released
        directors = ', '.join(directors)
        return '{0} ({1}, {2})'.format(movie.title, directors, year)

    def find_movie(self, title, year):
        movie = None
        try:
            movie = self.session.query(Movie, Media).\
                filter_by(title=title).\
                filter(
                    Movie.year == year,
                    Movie.id == Media.id).\
                filter(and_(
                    Movie.people.any(Person.role == role),
                    Person.name.in_(directors))).\
                one()
        except alchemy_exceptions.SQLAlchemyError:
            return movie
        return movie

    @classmethod
    def is_movie(cls, root, name):
        log = getLogger('Rkive.Index')
        log.info("is_movie")
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


Base = declarative_base()

class Media(Base):
    __tablename__='media'
    id = Column(Integer, primary_key=True)
    filepath = Column(String)
    format = Column(String)

    def __init__(self, fp, fmt):
        self.filepath = fp
        self.format = fmt


class Movie(Base):
    __tablename__ = 'movie'
    Column('workid', Integer, primary_key=True)
    title = Column(String)
    category = Column(String)
    year = Column(String)
    mediaobjects = relationship(
        "Media",
        backref='movie',
        cascade="all, delete, delete-orphan"
    )

    def __init__(self, title, year):
        self.title = title
        self.year = year
        self.category = 'movie'
