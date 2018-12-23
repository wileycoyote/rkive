from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String

PersonBase = declarative_base()


class Person(PersonBase):
    __tablename__ = 'person'
    __table_args__ = {'schema': 'person'}
    id = Column(Integer, primary_key=True)
    published_name = Column(String)


class Book(PersonBase):
    __tablename__ = 'book'
    __table_args__ = {'schema': 'person'}
    id = Column(Integer, primary_key=True)
    people_id = Column(Integer, ForeignKey('Person.person.id'))
    book_id = Column(Integer, book_id)


class Movie(Base):
    __tablename__ = 'movie'
    __table_args__ = {'schema': 'person'}
    id = Column(Integer, primary_key=True)
    role = Column(String)
    people_id = Column(Integer, ForeignKey('person.id'))
    person = relationship("Person")
    movie_id = Column(Integer, "movie_id"))

    def __init__(self, r, p, m):
        self.role = r
        self.person = p
        self.movie_id = m
