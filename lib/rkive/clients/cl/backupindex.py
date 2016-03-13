from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declared_attr
from rkive.clients.files import visit_files
from rkive.clients.cl.opts import GetOpts
from rkive.clients.log import LogInit
import os.path
import hashlib
import os
import datetime
import sys

Base = declarative_base()
class Files(Base):
    __tablename__ = 'files'
    id =  Column('id', Integer, primary_key=True)
    filepath = Column('filepath', String(1000))
    mtime = Column('mtime', String(30))
    ctime = Column('ctime', String(30))

    def __init__(self, fph, ctime, mtime):
        self.filepath = fph
        self.ctime = ctime
        self.mtime = mtime


engine = create_engine('postgresql://postgres:postgres@192.168.1.155/BackupIndex')
Base.metadata.create_all(engine)
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)

class BackupIndex(object):

    def run(self, logloc=None):
        conn = engine.connect()
        self.session = Session(bind=conn)
        self.file_count = 0
        self.max_files = 2048
        try:
            go = GetOpts(parent=self)
            go.get_opts()
            self.console = True
            LogInit().set_logging(
                location=logloc, 
                filename='backupindex.log', 
                debug=self.debug, 
                console=self.console)
            print("Recursive: "+str(self.recursive))
            self.max_elements = len(self.base.split('/'))
            visit_files(
                folder=self.base, 
                recursive=self.recursive,
                funcs=[self.add_to_database])
            self.session.commit()
        except:             
            print( "Unexpected error:", sys.exc_info()[0])
            self.session.rollback()
            sys.exit()
        finally:
            self.session.close()

    def add_to_database(self, root, filename):
        # we need to take off the base to get a relative path 
        rp_leaves = root.split('/')
        rp = '/'.join(rp_leaves[self.max_elements:])
        fp = '/'.join([rp,filename])
        print("fp: "+fp)
        h = hashlib.md5()
        h.update(fp.encode())
        hfp = h.digest()
        ctime = str(datetime.datetime.fromtimestamp(os.stat(fp).st_ctime))
        mtime = str(datetime.datetime.fromtimestamp(os.stat(fp).st_mtime))
        f = Files(hfp, mtime, ctime)
        self.session.add(f)
        #
        # do a commit every so often to avoid a long commit at end
        self.file_count = self.file_count + 1
        if self.file_count%self.max_files:
            self.session.commit()
