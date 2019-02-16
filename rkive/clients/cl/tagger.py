import os.path
import subprocess
from logging import getLogger
import glob
import re
from rkive.index.musicfile import TypeNotSupported, FileNotFound
from rkive.index.musicfile import MusicFile, MusicTrack
from rkive.clients.files import visit_files


class Tagger(object):

    def __init__(self):
        self.cuesheet = None
        self.markdown = None
        self.pattern = None
        self.gain = None
        self.media = None
        self.recursive = False

    def run(self):
        log = getLogger('Rkive.Tagger')
        try:
            if self.cuesheet:
                self.modify_from_cuesheet()
                return
            if self.markdown:
                self.modify_from_markdown()
                return
            if self.pattern:
                self.modify_from_pattern()
                return
            if self.gain:
                self.search_and_modify_gain()
                return
            # now set the attributes for the media object
            self.media = MusicFile()

            if not self.media:
                log.fatal("No media object instanciated")
                raise

            # check arguments for something to add tags/to
            for t in MusicTrack.get_rkive_tags():
                if hasattr(self, t):
                    v = getattr(self, t)
                    log.debug("t: {0} v: {1}".format(t, v))
                    if v:
                        log.debug("t: {0} v: {1}".format(t, v))
                        setattr(self.media, t, v)

            if self.printtags:
                if self.filename:
                    self.media.set_media(self.filename)
                    self.report_file_tags()
                    return
                self.report_all_files()
                return

            if not self.media.__dict__:
                log.info("no attributes to apply")
                return

            if self.filename:
                folder, filename = os.path.split(self.file)
                self.modify_file_tags(folder, filename)
                return

            self.search_and_modify_files()
            return
        except TypeNotSupported:
            log.fatal("Type not supported")
        except FileNotFound:
            log.fatal("Type not supported")

    def report_file_tags(self, base, filename):
        log = getLogger('Rkive.Tagger')
        fp = os.path.join(base, filename)
        musicfile = MusicFile()
        musicfile.set_media(fp)
        if self.all_tags:
            log.info("Music Attributes for {0}".format(fp))
            musicfile.report_all_tags()
            return
        if self.no_tag:
            musicfile.report_unset_tags(self.no_tag)
        if self.tag:
            musicfile.report_set_tags(self.tag)

    def report_all_files(self):
        log = getLogger('Rkive.Tagger')
        log.info("print tags of music files in {0}".format(self.base))
        visit_files(
            folder=self.base,
            funcs=[self.report_file_tags],
            include=self.is_music_file,
            recursive=self.recursive)

    def search_and_modify_gain(self):
        visit_files(
            folder=self.base,
            funcs=[self.modify_gain],
            include=self.is_music_file)

    def modify_gain(self, root, filename):
        cmd = ['metaflac', '--add-replay-gain', filename]
        if filename.endswith('.mp3'):
            cmd = ['mp3gain', '-r', filename]
        subprocess.call(cmd, cwd=root)

    # assume that one pattern matches all the files under examination
    def modify_from_pattern(self):
        visit_files(
            folder=self.base,
            funcs=[self.mod_filetags_from_regexp],
            include=MusicFile.is_music_file,
            recursive=self.recursive)

    def mod_filetags_from_regexp(self, root, filename):
        (fn, ext) = os.path.splitext(filename)
        self.media = MusicFile()
        for t, v in self.pattern.match(fn).items():
            setattr(self.media, t, v)
        self.modify_file_tags(root, filename)

    def modify_from_cuesheet(self):
        log = getLogger('Rkive.Tagger')
        import audiotools.cue
        cue = audiotools.cue.read_cuesheet(self.cuesheet)
        (folder, base) = os.path.split(self.cuesheet)
        if (folder == ''):
            folder = os.getcwd()
        log.info("Using cuesheet {0} in folder {1}".format(base, folder))
        os.chdir(folder)
        files = glob.glob('*.flac')
        for filename in files:
            # shntool gives us this nice %t-%name filename
            file_number = re.search(r'(\d\d)', filename)
            if (not file_number):
                continue
            log.info(f"Setting attributes from cuesheet for file {filename}")
            tracknumber = int(file_number.group(0))
            # build the tag list
            # standard tags
            album_fields = cue.get_metadata().filled_fields()
            m = MusicFile()
            for a in album_fields:
                setattr(m, a[0], a[1])
            # tags unique to track
            for f in cue.track(tracknumber).get_metadata().filled_fields():
                setattr(m, f[0], f[1])
            m.tracknumber = str(tracknumber)
            m.filename = os.path.join(folder, filename)
            m.save()

    def set_tracks_from_markdown(self, filename):
        """ Markdown Format:
            line 1:<version>,<number of albums>,<album count>,
                <nr of titles/files>
            line 2:<tag>:<value>
            line 3:<tag>[tracknumber]:value
            line 4:<tag>[tracknumber-tracknumber+offset]:value
            :
            line <offset>:<tag>:value
            line ===TITLES===
            line <offset+1>: title
            :
            line <offset+1+nr of titles>:title
            line ===FILES===
            line <offset+nr of titles+2>:filepath
            :
            line <offset+nr of titles*2+3>:filepath
        """
        log = getLogger('Rkive.Tagger')
        log.debug("using file {0}".format(filename))
        with open(filename) as fh:
            header = fh.readline().strip()
            version, album_nr, album_count, nr_titles = header.split(',')
            nr_titles = int(nr_titles)
            self._tracks = {}
            while(1):
                x = fh.readline().strip()
                log.debug("line: {0}".format(x))
                if x.startswith('==='):
                    break
                tag, value = x.split(':', 1)
                log.debug("tag: {0}, value: {1}".format(tag, value))
                # these itmes belong to a subset of tracks
                if '[' in tag:
                    sqrbrkt = tag.index('[')
                    tag_name = tag[0:sqrbrkt]
                    tag_indices = tag[sqrbrkt+1:-1]
                    if '-' in tag_indices:
                        start, fin = tag_indices.split('-')
                        log.debug("start: {0} fin: {1}".format(start, fin))
                        for k in range(int(start)-1, int(fin)):
                            if not (k in self._tracks):
                                self._tracks[k] = {}
                            self._tracks[k][tag_name] = value
                            log.debug("{0} {1}".format(self._tracks[k], k))
                    else:
                        tag_indices = int(tag_indices)-1
                        if not (tag_indices in self._tracks):
                            self._tracks[tag_indices] = {}
                        self._tracks[tag_indices][tag_name] = value
                else:
                    # these items belong to all tracks
                    for j in range(0, nr_titles-1):
                        if not (j in self._tracks):
                            self._tracks[j] = {}
                        self._tracks[j][tag] = value
            # pick up the titles
            i = 0
            while(1):
                x = fh.readline().strip()
                if x.startswith('==='):
                    break
                if not (i in self._tracks):
                    self._tracks[i] = {}
                self._tracks[i]['title'] = x
                self._tracks[i]['tracknumber'] = str(i+1)
                i = i+1
            # pick up the filenames
            i = 0
            while(1):
                x = fh.readline().strip()
                if not x:
                    break
                if not (i in self._tracks):
                    self._tracks[i] = {}
                self._tracks[i]['filename'] = x
                i = i+1

    def dump_tracks(self):
        log = getLogger('Rkive.Tagger')
        log.debug("Dumping Tracks")
        for k in sorted(self._tracks.keys()):
            v = self._tracks[k]
            log.debug("Dump Track {0}".format(k))
            for tag, value in v.items():
                log.debug("tag: {0} value: {1}".format(tag, value))
                
    def modify_from_markdown(self):
        log = getLogger('Rkive.Tagger')
        self.set_tracks_from_markdown(self.markdown)
        log.info("Modifying select files markdown {0}".format(self.markdown))
        if self.dryrun:
            log.info("Dryrun: Dumping tracks for {0}".format(self.markdown))
            self.dump_tracks()
            return
        for indx, track in self._tracks.items():
            m = MusicFile()
            log.info("index {0}".format(indx))
            log.info("Modifying file {0}".format(track['filename']))
            for tag, value in track.items():
                setattr(m, tag, value)
            m.save()

    def modify_file_tags(self, root, filename):
        log = getLogger('Rkive.Tagger')
        fp = os.path.join(root, filename)
        if self.dryrun:
            log.info("Dryrun: Proposed tags to modify on file {0}".format(fp))
            for t, v in self.media.__dict__.items():
                log.info("Tag to set: {0} Value: {1}".format(t, v))
            return
        log.info("modifying tags of file {0}".format(fp))
        try:
            self.media.filename = os.path.join(root, filename)
            self.media.save()
        except TypeNotSupported:
            log.warn("Type {0} not supported".format(fp))
            return
        except AttributeError as e:
            log.warn("Attribute error {0} with {1}".format(e, fp))
            return

    def search_and_modify_files(self):
        log = getLogger('Rkive.Tagger')
        log.info("modify tags of music files in {0}".format(self.base))
        visit_files(
            folder=self.base,
            funcs=[self.modify_file_tags],
            include=MusicTrack.is_music_file,
            recursive=self.recursive)


if __name__ == '__main__':
    Tagger().run()
