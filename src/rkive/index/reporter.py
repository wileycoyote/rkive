from rkive.index.musicfile import MusicFile, is_music_file
from logging import getLogger
from rkive.clients.files import visit_files

class Reporter(object):

    def all_tags(self, fp):
        log = getLogger('Rkive.Reporter')
        log.info("Music Attributes for {0}".format(fp))
        MusicFile().pprint(fp)

    def print_folder(self, base, recursive):
        log = getLogger('Rkive.Reporter')
        log.info("print tags of music files in {0}".format(base))
        visit_files(
            folder=base,
            funcs=[self.print_file_tags],
            include=is_music_file,
            recursive=recursive)
