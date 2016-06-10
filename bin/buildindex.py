#!/usr/bin/env python
from rkive.clients.files import visit_files
import os.path
import sys
from rkive.index.schema import Base, Movie
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlite3 import dbapi2 as sqlite
movies = set()
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
Movie.session = session
#
# the function that visit_files uses to store films in database
def index_movies(root, name):
    fp = '/'.join([root, name])
    path, leaf=os.path.split(fp)
    dp, idx = os.path.split(path)
    if idx in movies:
        return
    if Movie.is_movie(idx):
        movies.add(idx)

root='/media/azure/Multimedia/Movies/'
visit_files(folder=root, funcs=[index_movies],recursive=True)
movies_in_db = Movie.get_movies_index()
movies_in_db_rem = movies_in_db-movies_in_db
if movies_in_db_rem:
    print("Removing movies from db")
    Movie.remove_movies()
