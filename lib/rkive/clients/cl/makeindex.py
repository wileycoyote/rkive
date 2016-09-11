import rkive.clients.log
import rkive.clients.cl.opts
import os.path
import argparse
from logging import getLogger
import sys
from rkive.index.musicfile import MusicFile
from rkive.index.indexer import Indexer



class IndexClient(GetOpts):

    def __init__(self, logloc=None, engine=engine):
        Base.metadata.create_all(engine)
        Base.metadata.bind = engine
        self.session = sessionmaker(bind=engine)
        try:
            self.base = '.'
            p = self.get_parser()
            p.add_argument('--display',action='store_true',default=False)
            p.add_argument('--type',)
            p.add_argument('--location')
            p.add_argument('--make')
            p.parse_args(namespace=self)
            LogInit().set_logging(location=logloc,filename='index.log', debug=self.debug, console=self.console)
            if self.make:
                if self.index_type == 'music':
                    visit_files(base=self.base, funcs=[self.add_file_to_index], include=['.mp3','.flac'])
                return
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            self.session.rollback()
            sys.exit()
        finally:
            self.session.close()

    def add_file_to_index(self, fp):
        log = getLogger('Rkive')
        if self.dryrun:
            log.info('would index {0}'.format(fp))
            return
        m = rkive.index.mediaindex.MusicTrack(fp)
        rkive.index.mediaindex.DBSession.add(m)
