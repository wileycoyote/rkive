""" Module containing Person Classes for databases and micro-service """
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from flask import Flask, request

app = Flask(__name__)
PersonBase = declarative_base()


class Person(PersonBase):
    """ Basic Person Class """
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    published_name = Column(String)
    familyname = Column(String)
    firstname = Column(String)

    def __init__(self, familyname, firstname):
        self.familyname = familyname
        self.firstname = firstname


class Role(PersonBase):
    """ SQLAlchemy interface for multiple roles - 1 to many """
    __tablename__ = 'role'
    id = Column(Integer, ForeignKey('person.id'))
    title = Column(String)
    media_type = Column(String)
    media_title = Column(String)


class PersonDAO:  # pylint: disable=too-few-public-methods
    """ API for accessing Person Database """


class Director(PersonDAO):  # pylint: disable=too-few-public-methods

    def __init__(self):
        """ """

    def get_movie_director(self, person_id):
        """ Given an id, return a director"""

    def set_movie_director(self, forename, surname):
        """ Add a film director """


class PersonService:
    """ Flask servive front-end for person microservice"""

    @app.route("/director/movie/<int:person_id")
    def director(self, person_id):
        return Director.get_movie_director(person_id)

    @app.route("/director/movie/match", methods=['GET'])
    def directors(self):
        surname = request.args.get('surname')
        forename = request.args.get('forename')

    @app.route("director/movie/add")
    def set_director(self, methods=['GET']):
        surname = request.args.get('surname')
        forename = request.args.get('forename')
        return id
