import os
import rkive.index.mediaindex
from rkive.clients.files import Files

class Indexer(object):

    def run(self, base='.'):
        Files().visit(base=base, funcs=[self.add_file_to_index], exclude=self.exclude)

    def add_file_to_index(self, path, filename):
        full_path = os.path.join(path, filename)
        m = rkive.index.mediaindex.MusicTrack(full_path)
        rkive.index.mediaindex.DBSession.add(m)

    def exclude(self, path, file_name):
        for t in rkive.index.musicfile.MusicFile.types:
            if (file_name.endswith(t)):
                return False
        return True
