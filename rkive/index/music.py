from logging import getLogger

class MusicTrack():

    def __init__(self, session):
        self.session = session


class AlbumDataAccessor(AlbumSchema):

    def __init__(self, session):
        self.session = session

    def is_album(self, indx):
        return self.session.query(Album).filter(Album.index=indx)

    @property
    def album(self, indx, track):
        if not self.is_album(indx):
            album = AlbumSchema(
                index = indx,
                title=track.title, 
                subtitle=track.subtitle, 
                discumber=track.discnumber, 
                tracktotal=track.tracktotal, 
            )
            return album
        else:
           pass 


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
        track = MusicTrack(self.session, self._album, fp)
        self.tracks.append(track)
        self._album = self.album(indx, track)
        self._albumset = AlbumSet(self.indx, self._album)
