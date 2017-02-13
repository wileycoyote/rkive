from logging import getLogger

class Index(object):

    def __init__(self, base, session):
        self.base = base
        self.session = session


class Movies(Index):

    def __init__(self, base, session):
        super(Movies, self).__init__(base, session)

    def make(self):
        movies = Movies(self.session)
        log.info("looking at {0}".format(source))
        movies_on_disk = set()
        for o in os.listdir(source):
            fp=os.path.join(source, o)
            if os.path.isdir(fp) and Movies.is_movie(source, o):
                if not fp in movies_on_disk:
                    movies_on_disk.add(fp)
        movies_in_db = movies.get_movies_index()
        if len(movies_on_disk)==0:
            log.warn("No movies found on disk")
            return
        if movies_in_db == movies_on_disk:
            log.info("Movies in db same as movies on disk, complete")
            return
        for m in movies_on_disk:
            dp,midx=os.path.split(m)
            title, directors, year=movies.parse_midx(midx) 
            log.info("title: {0} directors: {1} year: {2}".format(title,directors,year))
            movies.add_movie(title, directors, year, m) 

class Music(Index):

    def __init__(self, base, session):
        super(Movies, self).__init__(base, session)

    def make(self):
        visit_files(folder=source,funcs=[self.add_music_to_index],recursive=True,include=rkive.index.musicfile.MusicFile.is_music_file)

    def add_music_to_index(self, fp):
        log = getLogger('Rkive.Index')
        log.info('would index {0}'.format(fp))
        if self.dryrun:
            log.info('would index {0}'.format(fp))
            return
        log.info('indexing {0}'.format(fp))
        m = rkive.index.schema.MusicTrack(fp)
        self.session.add(m)
        self.session.commit()
