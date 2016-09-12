import rkive.clients.log
import rkive.clients.cl.opts
import os.path
import argparse
from logging import getLogger
import sys
from rkive.musicfile import MusicFile
import rkive.clients.files


class ReportClient(Report, FileSanitiser):

    def run(self, log=None):
        try:
            go = rkive.clients.cl.opts.GetOpts(parent=self)
            go.p.add_argument('--sanitize', help="Sanitize filenames", action='store_true')           
            go.p.add_argument('--genre', help="Report on genre in music files in upload area", action='store_true')
            go.p.add_argument('--no-genre', help="Report on music files with no genre in upload area", action='store_true')
            go.p.add_argument('--summary', help="Summary of files in upload area", action='store_true')
            go.get_opts()
            rkive.clients.log.LogInit().set_logging(location=log,filename='uploader.log', debug=self.debug, console=self.console)
            if (self.sanitize):
                self.sanitize_files()
                return
            if (self.genre):
                self.report_genre()
                return
            if (self.no_genre):
                self.report_no_genre()
                return
            if (self.summary):
                self.list_summaries()
        except SystemExit:
            pass

  
