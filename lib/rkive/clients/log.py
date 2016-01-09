import logging
import logging.config
import os

class LogInit(object):
    def __init__(self):
        self.formatter = ''
        self.level = logging.INFO
        self.handlers = {}
        self.root = {}
        self.loggers = {}

    def get_dict(self):
        return {
            'version' : 1,
            'handlers' : self.__dict__['handlers'],
            'root' : self.__dict__['root'],
            'loggers' : self.__dict__['loggers']
        }

    def set_debug(self):
        self.level = logging.DEBUG

    def set_root(self):
        self.root['level'] = self.level
        self.root['formatter'] = self.formatter

    def set_stdout_handler(self):
        self.handlers['stdout_handler'] = {
            'class': 'logging.StreamHandler', 
            'stream': 'ext://sys.stdout'
        }

    def set_file_handler(self, fn):
        self.handlers['fileout'] = {
            'class' : 'logging.FileHandler',
            'filename': fn
        }
   
    def set_logger(self):
        h = []
        for n in self.handlers:
            h.append(n)
        self.loggers['Rkive'] = {
            'handlers' : h,
            'propagate' : True,
            'level' : self.level
        }
        self.loggers['paramiko.transport'] = {        
            'handlers' : h,
            'propagate' : True,
            'level' : self.level 
        }
        self.loggers['sqlalchemy.engine'] = {
            'handlers' : h,
            'propagate' : True,
            'level' : self.level
        }

    def set_logging(self, location=None, filename=None, debug=False, console=True):
        if (debug):
            self.set_debug() 
        self.set_root()
        if (console):
            self.set_stdout_handler()
        filename = os.path.join(location, filename)
        self.set_file_handler(filename)
        self.set_logger()
        logging.config.dictConfig(self.get_dict())

    
