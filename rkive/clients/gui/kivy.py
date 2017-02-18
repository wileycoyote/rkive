from rkive.clients.log import LogInit
from rkive.clients.cl.opts import GetOpts
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
from kivy.uix.listview import ListView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.uix.label import Label

class MasterDetailView(GridLayout):
    pass
