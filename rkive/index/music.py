from rkive.index.music import MusicFile

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String, ForeignKey, relationship

MusicBase = declarative_base()


class Music(MusicFile):

    def __init__(self, session):
        self.session = session
        self._index = ''
        self._album_set = False

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, fp):
        fields = fp.split('/')
        if fields:
            self._album_set = True
        self._file_path = fp

    @property
    def track(self, fp):
        self.media = self._file_path
        self._track = Music()

    @property
    def album_set(self):
        return self._album_set

    @property
    def album(self, indx, track):
        album = self.session.query(Music).filter(Music.index == indx)
        if not album:
            album = Music(
                index=indx,
                title=track.title,
                subtitle=track.subtitle,
                discumber=track.discnumber,
                tracktotal=track.tracktotal,
            )
            return album
        return album


class Media(MusicBase):
    __tablename__ = 'musicmedia'
    id = Column(Integer, primary_key=True)
    media_id = Column(Integer, ForeignKey('media.id'))
    file = relationship("File")
    musictrack_id = Column(Integer, ForeignKey("musictrack.id"))
    musictrack = relationship('Musictrack')

    def __init__(self, m, f):
        self.musictrack = m
        self.file = f


class Musictrack(MusicBase):
    __tablename__ = 'musictrack'
    people = relationship(
        "Musicpeople",
        backref='musictrack',
        cascade="all, delete, delete-orphan")
    mediaobjects = relationship(
        "Musicmedia",
        backref='musictrack',
        cascade="all, delete, delete-orphan")
    id = Column('id', Integer, primary_key=True)
    Column('albumname', String, primary_key=True)
    Column('series_number', Integer, primary_key=True)
    Column('tracknumber', Integer, primary_key=True)
    Column('attrname', String)
    Column('attrval', String)

    def __init__(self, path):
        """ Init the class """
