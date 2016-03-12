from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declared_attr
from rkive.clients.files import visit_files
from rkive.clients.cl.opts import GetOpts, FolderValidation, FileValidation
from rkive.clients.log import LogInit

class Files(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id =  Column(Integer, primary_key=True)
    filepath = Column(String(1000))
    modtime = Column(String(20))

Base = declarative_base(cls=Files)

engine = create_engine('postgresql://postgres:postgres@192.168.1.155/MediaIndex')
Base.metadata.create_all(engine)
Base.metadata.bind = engine

class BackupIndex(object):

    def run(self, logloc=None):
        DBSession = sessionmaker()
        DBSession.bind = engine
        db = DBSession()
        try:
            go = GetOpts(parent=self)
            go.p.parse_args()
            go.get_opts()
            self.console = True
            LogInit().set_logging(
                location=logloc, 
                filename='backupindex.log', 
                debug=self.debug, 
                console=self.console)
            visit_files(
                folder=self.base, 
                recursive=self.recursive,
                funcs=[self.add_to_database])
        except SystemExit:
            pass
    
    def add_to_database(self, root, filename):
        pass
