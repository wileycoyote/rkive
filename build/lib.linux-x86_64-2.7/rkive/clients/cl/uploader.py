import rkive.clients.log
import rkive.clients.cl.opts
from rkive.distribution.manager import Distributer
import os.path
import argparse
from logging import getLogger

class DistributerClient(Distributer):

    def __init__(self, rerun=False):
        self.rerun = rerun

    def run(self, log=None):
        try:
            go = clients.cl.opts.GetOpts(parent=self)
            go.p.add_argument('--base', required=True, nargs=1, help="full path to base of files", action=client.cl.opts.BaseAction)
            go.p.add_argument('--populate-base', help="Create base", action='store_true')
            go.p.add_argument('--run', help='Copy files', action='store_true')
            go.get_opts()
            clients.log.LogInit().set_logging(location=log,filename='distributer.log', debug=self.debug, console=self.console)
            if (self.populate_base):
                self.create_base()
                return
            if (self.run):
                self.distribute_files()
                return
        except SystemExit:
            pass
