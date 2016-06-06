#!/usr/bin/env python
from rkive.clients.files import visit_files
import os.path
import re
from rkive.index.schema import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlite3 import dbapi2 as sqlite
movies={}


film_re = re.compile('(.*?) \((.*?), (\d\d\d\d)\)')

def index_movies(root, name):
    fp = '/'.join([root, name])
    path, leaf=os.path.split(fp)
    dp, ld = os.path.split(path)
    if ld in movies:
        return
    m = film_re.match(ld)
    if m:
        movie = m.group(1)
        director = m.group(2)
        year = m.group(3)
        movies[ld] = Movie(movie, director, year)

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
#engine = create_engine('postgresql://postgres:postgres@192.168.1.155/MediaIndex')
dburi='sqlite+pysqlite:////home/roger/Projects/Rkive/data/index.db'
print(dburi)
engine = create_engine(dburi, module=sqlite)
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker()
DBSession.bind = engine
db = DBSession()    

root='/media/azure/Multimedia/Movies/'
visit_files(folder=root, funcs=[index_movies],recursive=True)
for m in movies.values():
    m.set_session(db)
    m.p()
    m.save()
