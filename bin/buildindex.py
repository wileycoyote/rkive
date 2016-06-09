#!/usr/bin/env python
from rkive.clients.files import visit_files
import os.path
import re
import sys
from rkive.index.schema import Base, Movie
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlite3 import dbapi2 as sqlite
#
# structure for storing films the have already been store in database
movies={}
#
# folder format is '<title> (<director_1, director_2 ... director_x>, <year>)'
film_re = re.compile('(.*?) \((.*?), (\d\d\d\d)\)')
# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
#engine = create_engine('postgresql://postgres:postgres@192.168.1.155/MediaIndex')
dburi='sqlite+pysqlite:////home/roger/Projects/Rkive/data/index.db'
engine = create_engine(dburi, module=sqlite)
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()    
#
# the function that visit_files uses to store films in database
def index_movies(root, name):
    fp = '/'.join([root, name])
    path, leaf=os.path.split(fp)
    dp, idx = os.path.split(path)
    if idx in movies:
        return
    m = film_re.match(idx)
    if m:
        movies[idx] = 1
        movie = m.group(1)
        director = m.group(2)
        year = m.group(3)
        directors = director.split(', ')
        if Movie.find_movie(session, m.title, 'mkv',year,directors):
            print('Movie {0} found'.format(idx))
            return
        print("Insert new film {0} into database".format(idx))
        m = Movie(movie, directors, year)
        m.set_db(session)
        m.save()

root='/media/azure/Multimedia/Movies/'
visit_files(folder=root, funcs=[index_movies],recursive=True)
   
