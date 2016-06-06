from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Table

Base = declarative_base()

association_table = Table('association', Base.metadata,
    Column('opus_id', Integer, ForeignKey('opus.id')),
    Column('participant_id', Integer, ForeignKey('participant.id'))
)

class Opus(Base):
    __tablename__ = 'opus'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    participants = relationship("Participant",
                    secondary=association_table,
                    back_populates="opii")
    category = Column(String)
    mediaobjects = relationship("Media")

    def __init__(self, t, c, p):
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
    media = Column(String)
    year_produced = Column(String)
    year_released = Column(String)
    year_reissued = Column(String)
    media_type = Column(String)

    def __init__(self, mt, y):
        self.media_type = m
        self.year_released = y

class Movie(object):

    def __init__(self, title, director, year):
        self.title = title
        self.director = director
        self.year = year
        self.category = 'movie'
        self.role = 'director'

    def p(self):
        print("{0}, ({1}, {2})".format(self.title, self.director, self.year))

    def set_db(self, db):
        self.db = db
        
    def save(self):
        m = Media('mkv',self.year)
        o = Opus(self.title, 'movie')
        p = Participant(self.director, 'director')
        p.opii.append(o)
        o.participants.append(p)
        o.mediaobjects.append(m)
        self.db.add(p)
        self.db.add(o)
        self.db.add(m)
        self.db.add(a)
        self.db.commit()
