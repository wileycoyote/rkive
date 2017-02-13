import os
import argparse
from logging import getLogger
from rkive.clients.log import LogInit
from rkive.clients.cl.opts import GetOpts, FolderValidation, FileValidation

class ParsePattern(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(ParsePattern, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        values = Regexp(values)
        setattr(namespace, self.dest, values)

class RkiveRunner(GetOpts):

    def __init__(self, script='', logfolder='', install_path='', media_server=''):
        self.script = script
        self.logfolder = logfolder
        self.install_path = install_path
        self.media_server = media_server

    def set_logger(self, filename='', debug=False, console=False):
        LogInit().set_logging(
            location=self.logfolder,
            filename=filename,
            debug=debug,
            console=console)

    def convert(self):
        from rkive.clients.cl.converter import ConvertClient
        c = ConvertClient()
        p = self.get_parser()
        p.add_argument(
            '--convert',
            help="",
            action='store_true')
        p.add_argument(
            '--split',
            nargs=1,
            help="name of cue file to be split",
            action=FileValidation)
        p.parse_args(namespace=c)
        self.set_logger('convert.log', c.debug, c.console)
        c.run()

    def tagger(self):
        p = self.get_parser()
        p.add_argument('--printtags', help="print files in current folder", action='store_true',default=False)
        p.add_argument('--tag', type=str, nargs='?', help="select tags which are set for printtag", action='append')
        p.add_argument('--no-tag', type=str, nargs='?', help="select tag which are not set for printing", action='append')
        p.add_argument('--all-tags', help="report all tags", action='store_true', default=False)
        p.add_argument('--filename',  type=str, help="file to set attributes", action=FileValidation)
        p.add_argument('--pattern', type=str, help="regex for matching patterns in filenames", action=ParsePattern)
        p.add_argument('--cuesheet', type=str, help="give a cue file for entering metadata", action=FileValidation)
        p.add_argument('--markdown', type=str, help="give file containing metadata", action=FileValidation)
        p.add_argument('--gain', help="add gain to music files", action='store_true')
        for t,v in MusicTrack.rkivetags.items():
            option = '--'+t
            p.add_argument(option, help=v, type=str)
        from rkive.clients.cl.tagger import Tagger
        tag = Tagger()
        p.parse_args(namespace=tag)
        self.set_logger('tag.log', console=tag.console, debug=tag.debug)
        tag.run()

    def make_local_index(self):
        from rkive.clients.cl.makeindex import MakeIndexClient
        from rkive.clients.config import Config
        p = self.get_parser()
        p.parse_args(namespace=self)
        self.set_logger('make_local_index.log', console=self.console, debug=self.debug)
        log = getLogger('Rkive.MakeIndex')
        log.info("make local index")
        c = Config(os.environ['HOME'])
        for connection in c.connections:
            log.debug("connection {0}".format(connection))
            if connection[-1] != 'live':
                continue
            if connection[0] == 'local':
                MakeIndexClient(url=connection[0], sources=sources).run()

    def make_index(self):
        from rkive.clients.cl.makeindex import MakeIndexClient
        from rkive.clients.config import Config
        p = self.get_parser()
        p.parse_args(namespace=self)
        self.set_logger('make_index.log', console=self.console, debug=self.debug)
        log = getLogger('Rkive.MakeIndex')
        log.info("make index")
        c = Config(os.environ['HOME'])
        for connection in c.connections:
            if connection[0] != 'live':
                continue
            if connection[2] == 'remote':
                MakeIndexClient(url=connection[1], sources=c.sources).run()

    def run(self):
        script = self.script
        if script == 'rk_tag':
            self.tagger()
        if script == 'rk_local_index_gui':
            from rkive.clients.cl.index import IndexClient
            uri = 'sqlite:///{0}data/index.db'.format(install_path)
            engine = create_engine(uri)
            index_client = IndexClient(engine=engine)
            if index_client.display == 'kivy':
                from kivy.base import runTouchApp
                from rkive.clients.kivy.index import MasterDetailView
                master_detail = MasterDetailView(index_client, width=800)
                runTouchApp(master_detail)
                return
        if script == 'rk_report':
            from rkive.clients.cl.reporter import ReportClient
            ReportClient().run()
        if script == 'markup':
            from rkive.clients.cl.markup import MarkupClient
            MarkupClient().run()
        if script == 'rk_convert':
            self.convert()
        if script == 'rk_make_local_index':
            self.make_local_index()
        if script == 'rk_make_index':
            self.make_index()
