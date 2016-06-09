#!/usr/bin/env python
from rkive.clients.files import visit_files
import os.path
import re
import sys
from rkive.index.schema import Base, Movie,Opus, Media, Participant
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, or_, and_
from sqlite3 import dbapi2 as sqlite
import sqlalchemy.exc as alchemy_exceptions

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
category='movie'
title='Laura'
fmt ='mkv'
year='1944'
directors = ['Preminger']
try:
    m=session.query(Opus, Media).\
            filter_by(category=category,title=title).\
            filter(Media.media_format==fmt,Media.year_produced==year,Opus.id==Media.id).\
            filter(and_(Opus.participants.any(Participant.role=='director'), Participant.name.in_(directors))).\
            one()
except alchemy_exceptions.SQLAlchemyError:
    print("Not found")
    import sys
    sys.exit()
print(m[0].title,m[1].year_produced)
