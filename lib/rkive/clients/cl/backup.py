import os
from enum import Enum
import os.path
import hashlib
import datetime
import sys

from logging import getLogger
import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declared_attr
from rkive.clients.files import visit_files
from rkive.clients.cl.opts import GetOpts,FolderValidation
from rkive.clients.log import LogInit
import rkive.clients.log

Base = declarative_base()

class Artist(Base):
    __tablename__ = 'artists'
    id =  Column('id', Integer, primary_key=True)
    filepath = Column('filepath', String(1000))
    mtime = Column('mtime', String(30))
    ctime = Column('ctime', String(30))
    children = relationship("Collection")

    def __init__(self, fph, ctime, mtime):
        print(mtime)
        self.filepath = fph
        self.ctime = ctime
        self.mtime = mtime

class Collection(Base):
    __tablename__ = 'collections'
    id =  Column('id', Integer, primary_key=True)
    filepath = Column('filepath', String(1000))
    mtime = Column('mtime', String(30))
    ctime = Column('ctime', String(30))
    artist_id = Column('artist_id', Integer, ForeignKey("artists.id")) 
    children = relationship("File")

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
    column_id = Column('collection_id', Integer, ForeignKey("collections.id"), nullable=False)

    def __init__(self, collection_id, fph, ctime, mtime):
        self.filepath = fph
        self.ctime = ctime
        self.mtime = mtime
        self.collection_id = collection_id

engine = create_engine('postgresql://postgres:postgres@192.168.1.155/BackupIndex', echo='debug')
Base.metadata.create_all(engine)
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
log = getLogger('sqlalchemy').setLevel(logging.DEBUG)
class BackupIndex(object):

    def make_index(self):
        self.artists = {}
        self.collections = {}
        conn = engine.connect()
        self.session = Session(bind=conn)
        self.file_count = 0
        self.max_files = 2048
        self.max_elements = len(self.base.split('/'))-1
        try:
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
            raise
        finally:
            self.session.close()

    def add_to_database(self, root, filename):
        # we need to take off the base to get a relative path
        fp = os.path.join(root, filename)
        rp_leaves = fp.split('/')[self.max_elements+1:]
        print("2"+'/'.join(rp_leaves))
        artist, artist_id = self.add_artist(rp_leaves)
        collection = rp_leaves.pop(0)
        c_path = os.path.join(self.base,artist,collection)
        print("4")
        collection_id = self.add_collection(artist_id, c_path)
        self.add_file(collection_id, rp_leaves)
        #
        # do a commit every so often to avoid a long commit at end
        self.file_count = self.file_count + 1
        if self.file_count%self.max_files:
           self.session.commit() 

    def add_artist(self, rp_leaves):
        artist = rp_leaves[0]
        if artist in self.artists:
            return artist, arists[artist]
        path = os.path.join(self.base, artist)
        mtime = self.get_mtime(path)
        ctime = self.get_ctime(path)
        h = self.get_hash(artist)
        print(h)
        a = Artist(h, ctime, mtime)
        self.session.add(a)
        self.session.flush()
        self.session.refresh(a)
        self.artists[artist] = a.id
        return artist, a.id
    
    def add_collection(self, artist_id, collection, rp_leaves):
        key = '::'.join(rp_leaves[0:1])
        if key in self.collections:
            return self.collections[key]
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

    def get_hash(self, seed):
        m = hashlib.md5()
        m.update(seed.encode())
        return m.digest()

class Status(Enum):
    todo = 1
    done = 2

class Job(object):

    def __init__(self, relative_path='', base='', target='' ):
        self.relative_path = relative_path
        self.base = base
        self.target = target
   
    def action(self):
        pass

class Copy(Job):

    def action(self):
        self.copy()

    def copy(self):
        pass

class Remove(Job):

    def action(self):
        self.remove()

    def remove(self):
        pass

class BackupClient(BackupIndex, GetOpts):

    def run(self, logloc=""):
        try:
            p = self.get_parser()
            p.add_argument(
                '--target',
                nargs=1,
                help="base folder of backup sector",
                action=FolderValidation,
                required=False)
            p.add_argument(
                '--index',
                default=False,
                help="base folder of backup sector",
                action='store_true')
            p.parse_args(namespace=self)            
            rkive.clients.log.LogInit().set_logging(
                location=logloc, 
                filename='backup.log', 
                debug=self.debug, 
                console=self.console)
            if self.index:
                self.make_index()
                return
            self.work = []
            self.build_jobs()
            self.run_jobs()
        except SystemExit:
            pass
    
    def run_jobs(self):
        for job in self.work:
            job.action()

    def build_jobs(self, base, target):
        self.tier1_base = self.get_folders(base)
        self.tier1_tgt = self.get_folders(target)
        #first check to see if we have to copy stuff to the target
        for v in self.tier1_base:
            if not v in self.tier1_target:
                job = Copy(
                    relative_path = v,
                    base = base,
                    target = target)
                self.work.append(job)
        # check to see if we have to remove stuff from the target
        for v in self.tier1_target:
            if not v in self.tier1_target:
                job = Remove(
                        relative_path = v,
                        target = base
                        )
                self.work.append(job)
        # look for the files to copy
        self.tier2_base = {}
        self.tier2_tgt = {}
        visit_files(target, funcs=[add_file_to_tier2_base])
        visit_files(target, funcs=[add_file_to_tier2_tgt])
        for n,v in self.tier2_base.items():
            if not n in self.tier2_target:
                relative_path = '/'.join([n,v])
                job = Copy(
                    relative_path = relative_path,
                    base = base,
                    target = target)
                self.work.append(job)
            else:
                fp_base = os.path.join(base, n, v)
                fp_tgt - os.path.join(target, n, v)
                modt_base = os.stat(fp_base)[8]
                modt_tgt = os.stat(fp_tgt)[8]
                if modt_base > modt_tgt:
                    relative_path = '/'.join([n,v])
                    job = Copy(
                        relative_path=relative_path,
                        target=target
                        )
                    self.work.append(job)
        # now do the delete 
        for n,v in self.tier2_tgt.items():
            if not n in self.tier2_base:
                job = Remove(
                    relative_path=v)
                self.work.append(job)

    def add_file_to_tier2_base(self, root, filename):
        self.tier2_base[root] = filename

    def add_file_to_tier2_base(self, root, filename):
        self.tier2_tgt[root] = filename

    def get_folders(self, root, folder):
        folders = {}
        for root, dirs, files in os.walk(target, topdown=True):
            for d in dirs:
                folders[d] = os.path.join(root, d)
        return folders

