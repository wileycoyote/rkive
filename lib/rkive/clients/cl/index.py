import rkive.clients.log
import rkive.clients.cl.opts
import os.path
import argparse
from logging import getLogger
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
f = Movie.get_movies_full(session)

print(m[0].title,m[1].year_produced)

class IndexClient(object):

    def run(self, logloc=None):
        try:
            self.base = '.'
            go = rkive.clients.cl.opts.GetOpts(parent=self)
            go.get_opts()
            rkive.clients.log.LogInit().set_logging(location=logloc,filename='index.log', debug=self.debug, console=self.console)
        except SystemExit:
            pass
