import re
from logging import getLogger
from rkive.index.schema import Movie as Movie
from rkive.index.schema import Moviepeople as Moviepeople
from rkive.index.schema import Person as Person
from rkive.index.schema import Media as Media

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
            p = Person(d)
            self.session.add(p)
            mp = Moviepeople('director', p)
            self.session.add(mp)
            self.session.commit()
            people.append(mp)
        t ='mkv'
        log.info("add related info")
        media = Media(t, fp)
        self.session.add(media)
        self.session.commit()
        movie = Movie(title, year)
        movie.add_person(people)
        movie.add_media(media)
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
            log.debug(movie)
            info = self.get_movie_index(movie)
            movie_info.add(info)
        return movie_info

    def get_movie_index(self, movie):
        directors = []
        for p in movie.people:
            if p.role=='director':
                directors.append(p.name)
        year =''
        for m in movie.media:
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

