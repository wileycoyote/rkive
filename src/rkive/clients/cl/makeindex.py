import rkive.clients.log
import rkive.clients.cl.opts
import os.path
import argparse
from logging import getLogger
import sys
from rkive.index.musicfile import MusicFile
from rkive.index.schema import Base, Movie

class MakeIndexClient(GetOpts):

    def __init__(self, logloc=None, urls=[], sources=[]):
        try:
            p = self.get_parser()
            p.parse_args(namespace=self)
            LogInit().set_logging(location=logloc,filename='index.log', debug=self.debug, console=self.console)
            for url in urls:
                engine = create_engine(url)
                session = sessionmaker(bind=engine)
                Base.metadata.create_all(engine)
                Base.metadata.bind = engine
                for category, source in sources.items():
                    if category == 'music':
                        visit_files(base=source, funcs=[self.add_track_to_index], include=['.mp3','.flac'])
                    if category == 'movies':
                        self.movies = set()
                        visit_files(base=source, funcs=[self.add_movie_to_index])
                        movies_in_db = Movie.get_movies_index()
                        movies_in_db_rem = movies_in_db - self.movies()
                        if movies_in_db_rem:
                            Movie.remove_movies(self.movies)
                        for m in self.movies:
                            m.save()
            return
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            self.session.rollback()
            sys.exit()
        finally:
            self.session.close()

    def add_track_to_index(self, fp):
        log = getLogger('Rkive')
        if self.dryrun:
            log.info('would index {0}'.format(fp))
            return
        m = rkive.index.mediaindex.MusicTrack(fp)
        rkive.index.mediaindex.DBSession.add(m)

    def add_movie_to_index(self, fp):
        path, leaf=os.path.split(fp)
        dp, idx = os.path.split(path)
        if idx in self.movies:
            return
        if Movie.is_movie(idx):
            self.movies.add(idx)

