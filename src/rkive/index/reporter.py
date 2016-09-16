from rkive.index.musicfile import MusicFile
from logging import getLogger

class Reporter(object):


    def is_music_file(self, fp):
        for t in Tags.Types:
            if (fp.endswith(t)):
                return True
        return False

