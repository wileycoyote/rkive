from logging import getLogger
import os.path

class MusicTrack(Musicfile):

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
        artist = fields.pop(0)
        album = fields.pop(0)
        if fields:
            cd = fields.pop(0)
            self._album_set = True
        self._file_path = fp

    @property 
    def track(self, fp):
        self.media = self._file_path
        self._track = MusicTrackSchema()
        
    @property 
    def album_set(self):
        return self._album_set


class AlbumDataAccessor(AlbumSchema):

    def __init__(self, session):
        self.session = session

    @property
    def album(self, indx, track):
        album = self.session.query(Album).filter(Album.index=indx)
        if not album:
            album = AlbumSchema(
                index = indx,
                title=track.title, 
                subtitle=track.subtitle, 
                discumber=track.discnumber, 
                tracktotal=track.tracktotal, 
            )
            return album
        return album

class Album(AlbumDataAccessor):

    def __init__(self, session, fp):
        self.tracks = []
        self._fp = fp

    @property 
    def indx(self):
        self._indx = '/'.join(self._fp.split('/')[0:4])

    @property 
    def track(self):
        self._track = ''

    @track.setter
    def track(self, fp):
        self.indx = fp
        track = MusicTrack(self.session, fp)
        self._album = self.album(indx, track)
        self._albumset = AlbumSet(self.indx, self._album)
        self.tracks.append(track)
