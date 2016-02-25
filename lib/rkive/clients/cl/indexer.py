import rkive.clients.log
import rkive.clients.cl.opts
import os.path
import argparse
from logging import getLogger
import sys
from rkive.index.musicfile import MusicFile
from rkive.index.indexer import Indexer

class Indexer:

    def run(self, logloc=None):
        try:
            self.base = '.'
            go = rkive.clients.cl.opts.GetOpts(parent=self)
            go.p.add_argument('--base', required=True, nargs=1, help="full path to base of files", action=rkive.clients.cl.opts.BaseAction)
            go.get_opts()
            rkive.clients.log.LogInit().set_logging(location=log,filename='index.log', debug=self.debug, console=self.console)
            visit_files(base=self.base, funcs=[self.add_file_to_index], include=['.mp3','.flac'])            
        except SystemExit:
            pass

    def add_file_to_index(self, fp):
        log = getLogger('Rkive')
        if self.dryrun:
            log.info('would index {0}'.format(fp))
            return
        m = rkive.index.mediaindex.MusicTrack(fp)
        rkive.index.mediaindex.DBSession.add(m)
