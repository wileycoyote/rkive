import rkive.clients.log
import rkive.clients.cl.opts
import os.path
import argparse
from logging import getLogger
import sys
from rkive.index.musicfile import MusicFile
from rkive.index.index import Index

class IndexClient(Index):

    def run(self, log=None):
        try:
            go = rkive.clients.cl.opts.GetOpts(parent=self)
            go.p.add_argument('--base', required=True, nargs=1, help="full path to base of files", action=rkive.clients.cl.opts.BaseAction)
            go.p.add_argument('--dry-run', required=False, help="Do not add to database")
            go.p.add_argument('--debug', required=False, help="lots of logs")
            go.get_opts()
            rkive.clients.log.LogInit().set_logging(location=log,filename='index.log', debug=self.debug, console=self.console)
        except SystemExit:
            pass

          
