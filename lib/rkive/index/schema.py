from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Table
import sqlalchemy.exc as alchemy_exceptions
from sqlalchemy import create_engine, or_, and_

Base = declarative_base()

association_table = Table('association', Base.metadata,
    Column('opus_id', Integer, ForeignKey('opus.id')),
    Column('participant_id', Integer, ForeignKey('participant.id'))
)

class Opus(Base):
    __tablename__ = 'opus'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    category = Column(String)
    participants = relationship("Participant",
                    secondary=association_table,
                    back_populates="opii")
    mediaobjects = relationship("Media")

    def __init__(self, t, c):
        self.title = t
        self.category = c


class Participant(Base):
    __tablename__ = 'participant'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)
    opii = relationship(
        "Opus",
        secondary=association_table,
        back_populates="participants")

    def __init__(self, n, r):
        self.name = n
        self.role = r

class Media(Base):
    __tablename__= 'media'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('opus.id'))
    media_format = Column(String)
    year_produced = Column(String)
    year_released = Column(String)
    year_reissued = Column(String)

    def __init__(self, mfmt, yp, yr, yri):
        self.media_format = mfmt
        self.year_produced = yp
        self.year_released = yr
        self.year_reissued = yri

class Movie(object):

    def __init__(self, title, director, year):
        self.title = title
        self.director = []
        for d in director:
            self.director.append(d)
        self.year = year
        self.category = 'movie'
        self.role = 'director'

    def info(self):
        ds = []
        for d in self.director:
            ds.append(d)
        d = ds[0]
        if len(ds) >1:
            d =', '.join(ds)
        return("{0}, ({1}, {2})".format(self.title, d, self.year))

    def p(self):
        print(self.info())

    def set_db(self, db):
        self.db = db
        
    def save(self):
        m = Media('mkv',self.year,self.year,self.year)
        o = Opus(self.title, 'movie')
        for d in self.director:
            p = Participant(d, 'director')
            p.opii.append(o)
            o.participants.append(p)
        o.mediaobjects.append(m)
        self.db.add(p)
        self.db.add(o)
        self.db.add(m)
        self.db.commit()

    def get_movies(db):
        return db.query(Opus.title).filter_by(category='movie').all() 

    #
    # returns a list of <movie_name> (<director(s)>, <year>)
    def get_movies_full(db):
        movie_info = {}
        movies = db.query(Opus).filter_by(category='movie').all() 
        for movie in movies:
            info = Movie.get_index(movie)
            movie_info[info] = movie
        return movie_info

    def get_index_from_db(movie):
        directors = []
        for p in movie.participants:
            if p.role=='director':
                directors.append(p.name)
        year =''
        for m in movie.mediaobjects:
            if m.media == 'mkv':
                year = m.year_released
        directors = ', '.join(directors)
        return '{0} ({1}, {2})'.format(movie.name, directors, year)

    def find_movie(db, title, fmt, year,directors=[] ):
        category = 'movie'
        role='director'
        try:
            m=session.query(Opus, Media).\
            filter_by(category=category,title=title).\
            filter(Media.media_format==fmt,Media.year_produced==year,Opus.id==Media.id).\
            filter(and_(Opus.participants.any(Participant.role==director), Participant.name.in_(directors))).\
            one()
        except alchemy_exceptions.SQLAlchemyError:
            return False
        return True
