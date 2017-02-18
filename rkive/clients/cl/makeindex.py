from rkive.clients.log import LogInit
from rkive.clients.cl.opts import GetOpts
import os.path
import argparse
from logging import getLogger
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import rkive.index.index

class MakeIndexClient(object):

    def __init__(self, url='', sources=[]):
        """ Initialise class - logs, command-line parameters, urls and sources

        Attributes:
            urls: A list of urls, each url describing a database target
            sources: A dictionary of categories to folders, each folder containing music or movies
        """
        self.url = url
        self.sources = sources

    def run(self):
        """search the source folders that have been passed, into the databases
        currently only movies and music are supported
        """
        log = getLogger('Rkive.Index')
        try:
            log.info("Connection: {0}".format(self.url))
            engine = create_engine(self.url)
            self.session = sessionmaker()
            bound_session = session(bind=engine)
            rkive.index.schema.Base.metadata.create_all(engine)
            rkive.index.schema.Base.metadata.bind = engine
            index_type = ''
            for source, category in self.sources.items():
                if not os.path.isdir(source):
                    log.info("skipping {0}".format(source))
                    continue
                log.info("making index for location {0} category {1}".format(source, category))
                # now call the right function for the category to make index
                class_name = category[0].title()
                index_class = getattr(rkive.index.index, class_name)
                if index_class:
                    index_class(source, bound_session).make()
                else:
                    log.info("No class for {0}".format(class_name))
            return
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            self.session.rollback()
            sys.exit()
        finally:
            self.session.close()
