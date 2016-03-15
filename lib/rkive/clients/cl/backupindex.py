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

class Artist(Base):
    __tablename__ = 'artists'
    id =  Column('id', Integer, primary_key=True)
    filepath = Column('filepath', String(1000))
    mtime = Column('mtime', String(30))
    ctime = Column('ctime', String(30))
    children = relationship("Collections")

    def __init__(self, fph, ctime, mtime):
        self.filepath = fph
        self.ctime = ctime
        self.mtime = mtime

class Collection(Base):
    __tablename__ = 'collections'
    id =  Column('id', Integer, primary_key=True)
    filepath = Column('filepath', String(1000))
    mtime = Column('mtime', String(30))
    ctime = Column('ctime', String(30))
    Column('artist_id', Integer, ForeignKey("artists.id"), nullable=False), 
    children = relationship("Files")

    def __init__(self, artist_id, fph, ctime, mtime):
        self.filepath = fph
        self.ctime = ctime
        self.mtime = mtime
        self.artist_id = artist_id

class File(Base):
    __tablename__ = 'files'
    id =  Column('id', Integer, primary_key=True)
    filepath = Column('filepath', String(1000))
    mtime = Column('mtime', String(30))
    ctime = Column('ctime', String(30))
    Column('collection_id', Integer, ForeignKey("collections.id"), nullable=False)

    def __init__(self, collection_id, fph, ctime, mtime):
        self.filepath = fph
        self.ctime = ctime
        self.mtime = mtime
        self.collection_id = collection_id

engine = create_engine('postgresql://postgres:postgres@192.168.1.155/BackupIndex')
Base.metadata.create_all(engine)
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)

class BackupIndex(object):

    def __init__(self):
        self.artists = {}
        self.collections = {}

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
            self.max_elements = len(self.base.split('/'))-1
            visit_files(
                folder=self.base, 
                recursive=self.recursive,
                funcs=[self.add_to_database])
            self.session.commit()
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            self.session.rollback()
            sys.exit()
        finally:
            self.session.close()

    def add_to_database(self, root, filename):
        print("1")
        # we need to take off the base to get a relative path
        fp = os.path.join(root, filename)
        rp_leaves = fp.split('/')[self.max_elements+1:]
        print("2"+'/'.join(rp_leaves))
        artist_id = self.add_artist(rp_leaves)
        collection = rp_leaves.pop(0)
        c_path = os.path.join(self.base,artist,collection)
        print("4")
        collection_id = self.add_collection(artist_id, collection, c_path)
        self.add_file(collection_id, rp_leaves)
        #
        # do a commit every so often to avoid a long commit at end
        self.file_count = self.file_count + 1
        if self.file_count%self.max_files:
           self.session.commit() 

    def add_artist(self, rp_leaves):
        name = rp_leaves[0]
        print("name: "+name)
        if name in self.artists:
            return arists[name]
        else:
            path = os.path.join(self.base, artist)
            mtime = self.get_mtime(path)
            ctime = self.get_ctime(path)
            h = self.get_hash(path)
            a = Artist(h, ctime, mtime)
            self.session.add(a)
            self.session.flush()
            self.session.refresh(a)
            self.artists[name] = a.id
            return a.id
    
    def add_collection(self, artist_id, rp_leaves):
        key = '::'.join(rp_leaves[0:1])
        if key in self.collections:
            return self.collections[key]
        else:
            name = rp_leaves[1]
            path = os.path.join(self.base, rp_leaves[0], name) 
            mtime = self.get_mtime(path)
            ctime = self.get_ctime(path)
            h = self.get_hash(rp_leaves[1:])
            c = Collection(artist_id, h, ctime, mtime)
            self.session.add(c)
            self.session.flush()
            self.session.refresh(c)
            self.collections[key] = c.id
            return c.id

    def add_file(self, collection_id, rp_leaves):
        fp = os.path.join(self.base, rp_leaves)
        mtime = self.get_mtime(fp)
        ctime = self.get_ctime(fp)
        h = self.get_hash(fp)
        f = File(h, ctime, mtime)
        self.session.add(f)

    def get_mtime(self, fp):
        t = os.path.getmtime(fp)
        return datetime.datetime.fromtimestamp(t)

    def get_ctime(self, fp):
        t = os.path.getctime(fp)
        return datetime.datetime.fromtimestamp(t)

    def get_hash(self, rp_leaves):
        f = '/'.join(rp_leaves)
        m = hashlib.md5()
        m.update(f)
        return m.digest()
