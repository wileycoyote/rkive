from rkive.clients.log import LogInit
from rkive.clients.cl.opts import GetOpts
import os.path
import argparse
from logging import getLogger
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from rkive.index.index import Index

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
                bound_session = session(bind=engine)
                rkive.index.schema.Base.metadata.create_all(engine)
                rkive.index.schema.Base.metadata.bind = engine
                index_type = ''
                for source, category in self.sources.items():
                    if not os.path.isdir(source):
                        log.info("skipping {0}".format(source))
                        continue
                    index = Index(source, bound_session)
                    # now call the right function for the category to make index
                    if getattr(index, category[0].lower()):
                        getattr(index, category[0].lower())()
                    else:
                        log.info("No class for {0}".format(category))
            return
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            self.session.rollback()
            sys.exit()
        finally:
            self.session.close()
