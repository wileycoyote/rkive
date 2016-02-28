from rkive.distribution.clients.distributer import Distributer
from rkive.index.musicfile import MusicFile
from logging import getLogger

class Report(Distributer):

    min_char = 33
    max_char = 126

    def is_music_file(self, fp):
        for t in MusicFile.Types:
            if (fp.endswith(t)):
                return True
        return False

    def list_summaries(self):
        register = [
            self.summary_badchars,
            self.summary_low_filetag_count,
            self.summary_flac_cue_pair,
            self.summary_no_genre,
            self.summary_file_types
        ]
        log = getLogger('Rkive.Report')
        self.file_types = {}
        self.badchars_count = 0
        self.no_genre_count = 0
        self.low_filetag_count = 0
        self.flac_cue_pair_count = 0
        log.info("Compiling stats")
        self.visit(base=self.base, funcs=[register])
        log.info("Summary")
        log.info("Number of files with 1 or more bad characters in file name {0}".format(self.badchars_count))
        log.info("Number of files with 0 or 1 tag {0}".format(self.low_filetag_count)) 
        log.info("Possible flac/cue pairs {0}".format(self.flac_cue_pair_count))
        log.info("Number of files with no genre {0}".format(self.no_genre_count))
        log.info("Summary of file types")
        for k,v in self.file_types.items():
            log.info("Type: {0} Count: {1}".format(k,v))
        log.info('End Summary')

    def report_genre(self):
        log = getLogger('Rkive.Report')
        log.info("Begin Report: Genre")
        self.visit(base=self.base, funcs=[self.collect_genre])
        log.info('End Report')
        
    def collect_genre(self, fp):
        if (not self.is_music_file(fp)):
            return
        log = getLogger('Rkive.Report')
        m = MusicFile()
        m.set_media(fp)
        log.info("File {0} has genre: ".format(fp))
        t = m.get_tags()
        if ('genre' in t.keys()):
            log.info(t['genre'])
        elif ('GENRE' in t.keys()):
            log.info(t['GENRE'])
        elif ('TCON' in t.keys()):
            log.info(t['TCON'])
        else:
            log.warn("No genre set")
    
    def report_no_genre(self):
        log = getLogger('Rkive.Report')
        log.info("Begin Report: No Genre")
        self.visit(base=self.base, funcs=[self.collect_no_genre])
        log.info('End Report')

    def collect_no_genre(self, fp):
        log = getLogger('Rkive.Report')
        if (not self.is_music_file(fp)):
            return
        m = MusicFile() 
        m.set_media(fp)
        t = m.get_tags()
        if ('genre' in t.keys()):
            return
        elif ('GENRE' in t.keys()):
            return
        elif ('TCON' in t.keys()):
            return
        else:
            log.info("File {0} has no genre set".format(fp))

    def summary_no_genre(self, fp):
        log = getLogger('Rkive.Report')
        if (not self.is_music_file(fp)):
            return
        m = MusicFile() 
        m.set_media(fp)
        t = m.get_tags()
        if ('genre' in t.keys()):
            return
        elif ('GENRE' in t.keys()):
            return
        elif ('TCON' in t.keys()):
            return
        else:
            self.no_genre_count +=1
   
    def report_badchars(self):
        log = getLogger('Rkive.Report')
        log.info("Begin Report: No Genre")
        self.visit(base=self.base, funcs=[self.collect_badchars])
        log.info('End Report')
 
    def collect_badchars(self, fp):
        log = getLogger('Rkive.Report')
        errs = []
        for n in fp:
            if (sys.getsizeof(n)> 38):
                e = "Possible UNICODE problem with {0} {1}".format(fp, str(n))        
                errs.append(e)
                continue
            if (ord(n)<self.min_char and ord(n) > self.max_char):
                e = "Non-english character with {0} {1} {2}".format(fp, n, chr(j))
                errs.append(e)
        self.badchar_files[fp] = "\n".join(errs)

    def summary_badchars(self, fp):
        log = getLogger('Rkive.Report')
        for n in fp:
            if (sys.getsizeof(n)> 38):
                self.badchars_count += 1
                return
            if (ord(n)<self.min_char and ord(n) > self.max_char):
                self.badchars_count += 1
                return
    
    def summary_low_filetag_count(self, fp):
        log = getLogger('Rkive.Report')
        if (not self.is_music_file(fp)):
            return
        m = MusicFile() 
        m.set_media(fp)
        if (m.get_number_of_tags() <= 1):
            self.low_filetag_count += 1

    def filetags(self, fp):
        log = getLogger('Rkive')
        if (not self.is_music_file(fp)):
            return
        m = MusicFile()
        m.set_media(fp)
        log.info("report filetags for {0}".format(fp))
        m.pprint()

    def summary_flac_cue_pair(self, fp):
        log = getLogger('Rkive.Report')
        if fp.endswith('.cue'):
            (p, b) = os.path.split(fp)
            (n, ext) = b.rsplit('.', 1)
            flac = os.path.join(p, n+'.flac')
            if os.path.exists(flac):
                self.flac_cue_pair_count += 1

    def summary_file_types(self, fp):
        import os.path
        p, ext = os.path.splitext(fp)
        if (not ext):
            return
        if (self.file_types.has_key(ext)):
            c = self.file_types[ext] +1
            self.file_types[ext] = c
        else:
            self.file_types[ext] = 1

class FileSanitiser(Distributer):

    def sanitize_files(self):
        self.visit(base=self.base, func=[self.rename_file], exc=['.DS_Store'])
        self.create_sanitization_flag()

    def rename_file(self):
        import unicodedata
        n=''
        n = unicodedata.normalize('NFKD', n.decode('utf-8')).encode('ascii', 'ignore')

    def create_sanitization_flag(self):
        import datetime.datetime
        san_flag = os.path.join(self.base, 'sanitation_flag')
        with open(self.san_flag,"w") as f:
            datetimestamp = datetime.datetime.now()
            f.write(datetimestamp)
    
    def check_for_sanitization_flag(self):
        san_flag = os.path.join(self.base, 'sanitation_flag')
        if (os.path.exists(self.san_flag)):
            return True
        return False

