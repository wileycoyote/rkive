from logging import getLogger

class MusicTrack(DataObjecct):

    def __init__(self, session):
        self.session = session

class AlbumDataAccessor(DataObject):

    def __init__(self, session):
        self.session = session

    def is_album(self, fp):
        return self.session.query(Album).filter(Album.filepath=fp)

    @property
    def album(self, album_idx):
        self._album_idx = album_idx
        album = self.is_album(album_idx)
        if album:
            return album
        else:
            # create album
            pass

    @album.setter
    def album(self):



class Album(AlbumDataAccessor):

    def __init__(self, session, fp):
        self.tracks = []
        self._album_idx = None
        self.fp = fp

    @property 
    def album_idx(self, fp):
        self._album_idx = '/'.join(fp.split('/')[0:4])

    def add_track(self, fp):
        self.album_idx = fp
        self.album = self.get_album(self.album_idx)
        track = MusicTrack(fp)
        self.tracks.append(track)
