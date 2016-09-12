from rkive.distribution.clients.distributer import Distributer
from rkive.distribution.config import ConfigManager

class LocalDistributer(Distributer):
    
    def __init__(self):
        self.config()

    def put(self, src_fp):
        tgt_fp = self.build_target(src_fp)
        chunksize = 1024
        with open(src_fp, "rb") as s, open(tgt_fp, "wb") as t: 
            chunk = s.read(chunksize)
            while chunk:
                # Do stuff with byte.
                t.write(chunk)
                chunk = s.read(chunksize)

    def get(self):
        pass

    def config(self):
        pass

    def build_target(self, fp):
        pass

