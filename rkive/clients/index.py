import os.path
from logging import getLogger
from rkive.clients.files import visit_files
from rkive.index.musicfile import MusicFile
from rkive.index.movie import Movies as MovieIndex


class IndexClient(object):

    def __init__(self, session=None):
        """ Initialise class - logs, command-line parameters, urls and sources

        Attributes:
            session: live connection to database
        """
        self.session = session


class Movies(IndexClient):

    def __init__(self, session):
        super(Movies, self).__init__(session)

    def make(self, source):
        log = getLogger(__class__)
        movies = MovieIndex(self.session)
        movies_on_disk = set()
        for o in os.listdir(source):
            fp = os.path.join(source, o)
            if os.path.isdir(fp) and MovieIndex.is_movie(source, o):
                if fp not in movies_on_disk:
                    movies_on_disk.add(fp)
        movies_in_db = movies.get_movies_index()
        if len(movies_on_disk) == 0:
            log.warn("No movies found on disk")
            return
        if movies_in_db == movies_on_disk:
            log.info("Movies in db same as movies on disk, complete")
            return
        for m in movies_on_disk:
            dp, midx = os.path.split(m)
            title, directors, year = movies.parse_midx(midx)
            log.info(f"title: {title} directors: {directors} year: {year}")
            movies.add_movie(title, directors, year, m)


class Music(IndexClient):

    def __init__(self, session):
        super(Music, self).__init__(session)

    def make(self, source):
        visit_files(
            folder=source,
            funcs=[self.add_music_to_index],
            recursive=True,
            include=MusicFile.is_music_file)

    def add_music_to_index(self, fp):
        log = getLogger('Rkive.Index')
        log.info('would index {0}'.format(fp))
        if self.dryrun:
            log.info('would index {0}'.format(fp))
            return
        log.info('indexing {0}'.format(fp))
