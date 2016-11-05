from rkive.clients.log import LogInit
from rkive.clients.cl.opts import GetOpts
import os.path
import argparse
from logging import getLogger
import sys
from rkive.index.musicfile import MusicFile
import rkive.index.schema 
from rkive.index.schema import Movies
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from rkive.clients.files import visit_files
from rkive.index.musicfile import MusicTrack

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
        try:
            for connection in self.connections:
                log.info("Connection: {0}".format(connection))
                engine = create_engine(connection)
                session = sessionmaker()
                self.session = session(bind=engine)
                rkive.index.schema.Base.metadata.create_all(engine)
                rkive.index.schema.Base.metadata.bind = engine
                movies=Movies(self.session)
                for source, category in self.sources.items():
                    cat=category[0].lower()
                    if cat == 'music':
                        visit_files(folder=source,funcs=[self.add_music_to_index],recursive=True,include=rkive.index.musicfile.MusicFile.is_music_file)
                    if cat == 'movies':
                        log.info("looking at {0}".format(source))
                        movies_on_disk = set()
                        for o in os.listdir(source):
                            fp=os.path.join(source, o)
                            if os.path.isdir(fp) and rkive.index.schema.Movies.is_movie(source, o):
                                if not fp in movies_on_disk:
                                    movies_on_disk.add(fp)
                        movies_in_db = movies.get_movies_index()
                        if len(movies_on_disk)==0:
                            log.warn("No movies found on disk")
                            break
                        if movies_in_db == movies_on_disk:
                            log.info("Movies in db same as movies on disk, complete")
                            break
                        #movies_in_db_rem = movies_in_db - self.movies
                        #if movies_in_db_rem:
                        #    log.debug("Remove remainder databases {0}".format(movies_in_db_rem))
                        #    movies.remove_movies(self.movies_in_db_rem)
                        for m in movies_on_disk:
                            dp,midx=os.path.split(m)
                            title, directors, year=movies.parse_midx(midx) 
                            log.info("title: {0} directors: {1} year: {2}".format(title,directors,year))
                            movies.add_movie(title, directors, year, m) 
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
        log.info('would index {0}'.format(fp))
        if self.dryrun:
            log.info('would index {0}'.format(fp))
            return
        log.info('indexing {0}'.format(fp))
        m = rkive.index.schema.MusicTrack(fp)
        self.session.add(m)
        self.session.commit()

