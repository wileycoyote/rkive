import logging
import logging.config

class LogInit(object):

    def __init__(self):
        self._formatter = '%(filename)s %(lineno)d %(messsage)s'
        self._level = logging.INFO

    def config(self, debug, quiet, filename):
        if debug:
            self._level = logging.DEBUG
        handlers = {} 
        if not quiet:
            handlers['stdout_handler'] = {
                'class': 'logging.StreamHandler', 
                'stream': 'ext://sys.stdout'
            }
        if filename:
            handlers['fileout'] = {
                'class' : 'logging.FileHandler',
                'filename': filename
            }
        root = {}
        root['level'] = self._level
        root['formatter'] = self._formatter
        loggers = {}
        loggers['Rkive'] = {
            'handlers' : handlers,
            'propagate' : True,
            'level' : self._level,
            'formatter' : self._formatter
        }
        loggers['sqlalchemy.engine'] = {
            'handlers' : handlers,
            'propagate' : True,
            'level' : self._level,
            'formatter' : self._formatter
        }
        config = {
            'version' : 1,
            'handlers' : handlers,
            'root' : root,
            'loggers' : loggers,
            'formatter' : self._formatter
        }
        logging.config.dictConfig(config)
