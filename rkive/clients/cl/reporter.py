from rkive.clients.log import LogInit
import os.path
import argparse
from logging import getLogger
import sys
from rkive.clients.cl.opts import GetOpts
from rkive.index.musicfile import MusicFile, Tags
from rkive.index.reporter import Reporter

class ReportClient(GetOpts, Reporter):

    def run(self, log=None):
        try:
            p = self.get_parser()
            p.add_argument('--filename', help="Report on a music file", action='store_true')
            p.add_argument('--all', help="Report on all files", action='store_true')
            for t,v in Tags.TagMap.items():
                option = '--'+t
                comment = v['comment']
                p.add_argument(option, help=comment, type=str)
            p.parse_args(namespace=self)
            LogInit().set_logging(
                location=log,
                filename='reporter.log',
                debug=self.debug,
                console=self.console)

            if self.genre:
                self.report_genre()
                return

            if self.title:
                self.report_title()
                return

            if self.summary:
                self.summary()
                return
            log.warn("Tag not implemented")

        except SystemExit:
            pass
