from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, create_engine, Date
from sqlalchemy import create_engine, or_, and_
import re
from rkive.index.musicfile import MusicFile as MusicFile
from logging import getLogger


