from rkive.clients.log import LogInit
from rkive.clients.cl.opts import GetOpts
import os.path
import argparse
from logging import getLogger
import sys
from rkive.index.musicfile import MusicFile
from rkive.index.schema import Base, Movie
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class MakeIndexClient(GetOpts):

    def __init__(self, logfolder='.', connections=[], sources=[]):
        """ Initialise class - logs, command-line parameters, urls and sources

        Attributes:
            logloc: filepath location of log
            urls: A list of urls, each url describing a database target
            sources: A dictionary of categories to folders, each folder containing music or movies
        """
        p = self.get_parser()
        p.parse_args(namespace=self)
        LogInit().set_logging(location=logfolder,filename='index.log', debug=self.debug, console=self.console)
        self.connections = connections
        self.sources = sources

    def run(self):
        """search the source folders that have been passed, into the databases
        currently only movies and music are supported
        """
        log = getLogger('Rkive.Index')
        session=''
        try:
            for connection in self.connections:
                log.info("Connection: {0}".format(connection))
                engine = create_engine(connection)
                session = sessionmaker(bind=engine)
                Base.metadata.create_all(engine)
                Base.metadata.bind = engine
                for category, source in sources.items():
                    if category == 'music':
                        visit_files(base=source, funcs=[self.add_music_to_index], include=['.mp3','.flac'])
                    if category == 'movies':
                        self.movies = set()
                        visit_files(base=source, funcs=[self.add_movie_to_index])
                        movies_in_db = Movie.get_movies_index()
                        movies_in_db_rem = movies_in_db - self.movies()
                        if movies_in_db_rem:
                            log.debug("Remove remainder databases {0}".format(movies_in_db_rem))
                            Movie.remove_movies(self.movies_in_db_rem)
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

    def add_music_to_index(self, fp):
        log = getLogger('Rkive.Index')
        if self.dryrun:
            log.info('would index {0}'.format(fp))
            return
        m = rkive.index.mediaindex.MusicTrack(fp)
        rkive.index.mediaindex.DBSession.add(m)

    def add_movie_to_index(self, fp):
        log = getLogger('Rkive.Index')
        path, leaf=os.path.split(fp)
        dp, idx = os.path.split(path)
        if idx in self.movies:
            return
        if Movie.is_movie(idx):
            if self.dryrun:
                log.info("Would index {0}".format(fp))
                return
            self.movies.add(idx)
