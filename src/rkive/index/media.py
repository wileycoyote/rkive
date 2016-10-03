from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Table
import sqlalchemy.exc as alchemy_exceptions
from sqlalchemy import create_engine, or_, and_
import re

Base = declarative_base()

association_table = Table('association', Base.metadata,
    Column('opus_id', Integer, ForeignKey('opus.id')),
    Column('participant_id', Integer, ForeignKey('participant.id'))
)

class Opus(Base):
    __tablename__ = 'opus'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    category = Column(String)
    participants = relationship("Participant",
class MusicTrack(Base, MusicFile):
    __tablename__ = 'MusicTrack'
    id_track = Column('idMusicTrack', Integer, primary_key=True)
    Column('discnumber', String)
    Column('disctotal', String)
    Column('album', String)
    Column('title', String)
    Column('filepath', String)
    Column('tracktotal', String)
    Column('tracknumber', String)
    Column('artist', String, nullable=True)
    Column('albumartist', String, nullable=True)
    Column('genre', String, nullable=True)
    Column('composer', String, nullable=True)
    Column('comment', String, nullable=True)

    def __init__(self, path):
        MusicFile.__init__(path)
                    secondary=association_table,
                    back_populates="opii",
                    cascade="all, delete")
    mediaobjects = relationship("Media", cascade="all, delete, delete-orphan")

    def __init__(self, t, c):
        self.title = t
        self.category = c


class Participant(Base):
    __tablename__ = 'participant'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)
    opii = relationship(
        "Opus",
        secondary=association_table,
        back_populates="participants")

    def __init__(self, n, r):
        self.name = n
        self.role = r

class Media(Base):
    __tablename__= 'media'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('opus.id'))
    media_format = Column(String)
    year_produced = Column(String)
    year_released = Column(String)
    year_reissued = Column(String)

    def __init__(self, mfmt, yp, yr, yri):
        self.media_format = mfmt
        self.year_produced = yp
        self.year_released = yr
        self.year_reissued = yri


