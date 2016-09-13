import re
from rkive.index.media import Media as Media

class Movie(object):

    # folder format is '<title> (<director_1, director_2 ... director_x>, <year>)'
    film_re = re.compile('(.*?) \((.*?), (\d\d\d\d)\)')
    session = None

    def __init__(self, title, director, year):
        self.title = title
        self.director = []
        for d in director:
            self.director.append(d)
        self.year = year
        self.category = 'movie'
        self.role = 'director'

    def p(self):
        directors = ', '.join(self.directors)
        p='{0} ({1}, {2})'.format(self.title, directors, self.year)
        print(p)

    def save(self):
        m = Media('mkv',self.year,self.year,self.year)
        o = Opus(self.title, 'movie')
        for d in self.director:
            p = Participant(d, 'director')
            p.opii.append(o)
            o.participants.append(p)
        o.mediaobjects.append(m)
        Movie.session.add(p)
        Movie.session.add(o)
        Movie.session.add(m)
        Movie.session.commit()

    def get_movies():
        return Movie.session.query(Opus.title).filter_by(category='movie').all()

    #
    # returns a list of <movie_name> (<director(s)>, <year>)
    def get_movies_index():
        movie_info = set()
        movies = Movie.session.query(Opus).filter_by(category='movie').all()
        for movie in movies:
            info = Movie.get_movie_index(movie)
            movie_info.add(info)
        return movie_info

    def get_movie_index(movie):
        directors = []
        for p in movie.participants:
            if p.role=='director':
                directors.append(p.name)
        year =''
        for m in movie.mediaobjects:
            if m.media_format == 'mkv':
                year = m.year_released
        directors = ', '.join(directors)
        return '{0} ({1}, {2})'.format(movie.title, directors, year)

    def find_movie(title, fmt, year,directors=[] ):
        category = 'movie'
        role='director'
        movie = None
        try:
            movie=Movie.session.query(Opus, Media).\
            filter_by(category=category,title=title).\
            filter(Media.media_format==fmt,Media.year_produced==year,Opus.id==Media.id).\
            filter(and_(Opus.participants.any(Participant.role==role), Participant.name.in_(directors))).\
            one()
        except alchemy_exceptions.SQLAlchemyError:
            return movie
        return movie

    def is_movie(s):
        m = Movie.film_re.match(s)
        if not m:
            return False
        movie = m.group(1)
        director = m.group(2)
        year = m.group(3)
        directors = director.split(', ')
        if Movie.find_movie(movie, 'mkv', year, directors):
            return True
        m = Movie(movie, directors, year)
        m.save()
        return True

    def remove_movies(movies):
        for movie in movies:
            m = Movie.film_re.match(movie)
            title = m.group(1)
            directors = m.group(2).split(', ')
            year = m.group(3)
            movie_in_db = Movie.find_movie(title, 'mkv', year, directors)
            movie_in_db.delete(synchronize_session=True)


