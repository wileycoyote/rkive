import os
import sys
import argparse
from logging import getLogger
from rkive.clients.log import LogInit
from rkive.clients.cl.opts import GetOpts, FileValidation, Regexp
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from rkive.index.musicfile import MusicTrack
from rkive.index.schema import Base
import rkive.clients.cl.index


class ParsePattern(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(ParsePattern, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        values = Regexp(values)
        setattr(namespace, self.dest, values)


class RkiveRunner(GetOpts):

    def __init__(
            self,
            script='',
            logfolder='',
            install_path='',
            media_server=''):
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
        p.add_argument(
            '--printtags',
            help="print files in current folder",
            action='store_true',
            default=False)
        p.add_argument(
            '--tag',
            type=str,
            nargs='?',
            help="select tags which are set for printtag",
            action='append')
        p.add_argument(
            '--no-tag',
            type=str,
            nargs='?',
            help="select tag which are not set for printing",
            action='append')
        p.add_argument(
            '--all-tags',
            help="report all tags",
            action='store_true',
            default=False)
        p.add_argument(
            '--filename',
            type=str,
            help="file to set attributes",
            action=FileValidation)
        p.add_argument(
            '--pattern',
            type=str,
            help="regex for matching patterns in filenames",
            action=ParsePattern)
        p.add_argument(
            '--cuesheet',
            type=str,
            help="give a cue file for entering metadata",
            action=FileValidation)
        p.add_argument(
            '--markdown',
            type=str,
            help="give file containing metadata",
            action=FileValidation)
        p.add_argument(
            '--gain',
            help="add gain to music files",
            action='store_true')
        for t, v in MusicTrack.rkivetags.items():
            option = '--'+t
            p.add_argument(option, help=v, type=str)
        from rkive.clients.cl.tagger import Tagger
        tag = Tagger()
        p.parse_args(namespace=tag)
        self.set_logger('tag.log', console=tag.console, debug=tag.debug)
        tag.run()

    def index(self):
        from rkive.clients.cl.makeindex import IndexClient
        from rkive.clients.config import Config
        index_client = IndexClient()
        p = self.get_parser()
        p.add_argument(
            '--label',
            type=str,
            help="name of config element to run"
        )
        p.parse_args(namespace=index_client)
        self.set_logger(
            'index.log',
            console=index_client.console,
            debug=index_client.debug)
        log = getLogger('Rkive.Index')
        config_path = os.path.join(
            os.environ['HOME'],
            '.config',
            'rkive',
            'connections.yml'
        )
        c = Config()
        c.connections = config_path
        c.sources = config_path
        for connection in c.connections:
            if self.label != connection['label']:
                log.info("Skipping {0}".format(connection['label']))
            if connection['status'] != 'live':
                log.info("Connection {0} not live".format(connection['label']))
                continue
            try:
                log.info("Connection: {0}".format(connection['url']))
                engine = create_engine(connection['url'])
                self.session = sessionmaker()
                Base.metadata.create_all(engine)
                Base.metadata.bind = engine
                if self.operation == 'make':
                    log.info("make index")
                    for s, c in self.sources.items():
                        if not os.path.isdir(s):
                            log.info("skipping {0}".format(s))
                            continue
                        log.info(f"index for location {s} category {c}")
                        class_name = c[0].title()
                        index_class = getattr(
                            rkive.clients.cl.index,
                            class_name
                        )
                        if index_class:
                            index_class(s, self.session).make(s)
                        else:
                            log.info("No class for {0}".format(class_name))
                    return
                if self.operation == 'search':
                    log.info("search index")
                    return
            except Exception:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                self.session.rollback()
                sys.exit()
            finally:
                self.session.close()
            return

    def run(self):
        script = self.script
        if script == 'rktag':
            self.tagger()
        if script == 'rk_local_index_gui':
            from rkive.clients.cl.index import IndexClient
            uri = f'sqlite:///{0}data/index.db {self.install_path}'
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
        if script == 'rk_make_index':
            self.index()
