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
import kivy
kivy.require('1.0.6') # replace with your current kivy version !
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.uix.label import Label
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

class ListScreen(GridLayout):

    def __init__(self, **kwargs):
        f = Movie.get_movies_full(session)
        super(LoginScreen, self).__init__(**kwargs)
        self.cols = 2
        self.add_widget(Label(text='User Name'))
        self.username = TextInput(multiline=False)
        self.add_widget(self.username)
        self.add_widget(Label(text='password'))
        self.password = TextInput(password=True, multiline=False)
        self.add_widget(self.password)

class IndexClient(App):

    def build(self): 
        try:
            go = rkive.clients.cl.opts.GetOpts(parent=self)
            go.get_opts()
            rkive.clients.log.LogInit().set_logging(location=logloc,filename='index.log', debug=self.debug, console=self.console)
        except SystemExit:
            pass
        return ListScreen()

