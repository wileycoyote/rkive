from dataclasses import dataclass
from typing import List
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey

BookBase = declarative_base()


@dataclass
class Book:
    isbn13: str
    title: str
    authors: List
    publisher: str
    year: str
    language: str
    category: str = ""


class BookPersistance(BookBase):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    publisher = Column(String)
    year = Column(str)
    language = Column(str)
    category = Column(str)


class BookAuthors(BookBase):
    __tablename__ = 'bookauthors'
    id = Column(Integer, primary_key=True)
    people_id = Column(Integer, ForeignKey('person.id'))
    book_id = Column(Integer, ForeignKey('book.id'))


class Person(BookBase):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    published_name = Column(String)
