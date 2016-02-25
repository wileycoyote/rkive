import os
import rkive.index.mediaindex
from rkive.clients.files import visit_files

class Indexer(object):

    def run(self, base='.'):
        visit_files(base=base, funcs=[self.add_file_to_index], include=['.mp3','.flac'])

    def add_file_to_index(self, path, filename):
        full_path = os.path.join(path, filename)
        m = rkive.index.mediaindex.MusicTrack(full_path)
        rkive.index.mediaindex.DBSession.add(m)
