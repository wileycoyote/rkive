from rkive.clients.cl.opts import GetOpts, BaseAction
import clients.log
import os.path
import argparse
from logging import getLogger
import clients.files

class Indexer(Index):

    def run(self):
        try:
            self.recursive = False
            go = GetOpts(parent=self)
            go.p.add_argument('--base', type=str, help="folder in which look for files", action=BaseAction)
            go.get_opts()
            self.console = True
            logs = 'logs/indexer.log'
            clients.log.LogInit().set_logging(location=log,filename='index.log', debug=self.debug, console=self.console)
            log = getLogger('Rkive.Indexer')
            if (not self.base):
                self.base='.'
            self.visit_files(self.add_to_index) 
        except SystemExit:
            pass
        except TypeNotSupported as e:
            log = getLogger('Rkive.Tagger')
            log.fatal("Type not supported")
        except FileNotFound as e:
            log = getLogger('Rkive.Tagger')
            log.fatal("Type not supported")

    def add_to_index(self, path):
        pass

