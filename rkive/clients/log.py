import logging
import logging.config


class LogInit(object):

    def __init__(self):
        self._formatter = '%(filename)s %(lineno)d %(messsage)s'
        self._level = logging.INFO
        self._quiet = True
        self._handlers = {}

    @property
    def console(self):
        return self._console

    @console.setter
    def console(self, on):
        if on:
            self._handlers['stdout_handler'] = {
                'class': 'logging.StreamHandler', 
                'stream': 'ext://sys.stdout'
            }
        else:
            del self._handlers['stdout_handler']

    @property
    def filepath(self):
        return self._filepath

    @filepath.setter
    def filepath(self, fp):
        self._handlers['fileout'] = {
            'class': 'logging.FileHandler',
            'filename': fp
        }

    def debug(self):
        self._level = logging.DEBUG

    def setup(self):
        root = {}
        root['level'] = self._level
        root['formatter'] = self._formatter
        loggers = {}
        loggers['Rkive'] = {
            'handlers': self._handlers,
            'propagate': True,
            'level': self._level,
            'formatter': self._formatter
        }
        loggers['sqlalchemy.engine'] = {
            'handlers': self._handlers,
            'propagate': True,
            'level': self._level,
            'formatter': self._formatter
        }
        config = {
            'version': 1,
            'handlers': self._handlers,
            'root': root,
            'loggers': loggers,
            'formatter': self._formatter
        }
        logging.config.dictConfig(config)
