import os.path
import argparse
from logging import getLogger
import glob
import re
from rkive.index.musicfile import MusicFile, Media, TypeNotSupported, FileNotFound
from rkive.clients.cl.opts import GetOpts, FolderValidation, FileValidation
import rkive.clients.regexp
from rkive.clients.files import visit_files
from rkive.clients.log import LogInit
import subprocess

class ParsePattern(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(ParsePattern, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        values = rkive.clients.regexp.Regexp(self.pattern)        
        setattr(namespace, self.dest, values)

class Tagger(GetOpts):

    def run(self, logloc=None):
        try:
            p = self.get_parser()
            p.add_argument('--printtags', help="print files in current folder", action='store_true',default=False)
            p.add_argument('--filename',  type=str, help="file to set attributes", action=FileValidation)
            p.add_argument('--pattern', type=str, help="regex for matching patterns in filenames", action=ParsePattern)
            p.add_argument('--cuesheet', type=str, help="give a cue file for entering metadata", action=FileValidation)
            p.add_argument('--markup', type=str, help="give file containing metadata", action=FileValidation)
            p.add_argument('--gain', help="add gain to music files", action='store_true')
            # need to construct a second 
            media_parser = argparse.ArgumentParser(parents=[p])
            self.media = MusicFile()
            for t,v in Media.TagMap.items():
                option = '--'+t
                comment = v['comment']
                media_parser.add_argument(option, help=comment, type=str)
            p.parse_args(namespace=self)
            media_parser.parse_args(namespace=self.media)
            LogInit().set_logging(location=logloc, filename='tagger.log', debug=self.debug, console=self.console)
            log = getLogger('Rkive.Tagger')
            if self.printtags:
                if hasattr(self, 'file'):
                    folder, filename = os.path.split(self.file)
                    self.print_file_tags(folder, filename)
                    return
                self.search_and_print_folder()
                return
            if self.cuesheet:
                self.modify_from_cuesheet()
                return
            if self.markup:
                self.modify_from_markup()
                return
            if self.pattern:
                self.modify_from_pattern()
                return
            if self.gain:
                self.search_and_modify_gain()
                return
            # check arguments for something to add tags/to
            hasargs = False
            for t in tags:
                if getattr(self, t):
                    hasargs = True
                    break
            if (not hasargs):
                log.info("no attributes to apply")
                return
            if (self.filename):
                folder, filename = os.path.split(self.file)
                self.modify_file_tags(folder, filename)
                return
            self.search_and_modify_files()
            return 
        except SystemExit:
            pass
        except TypeNotSupported as e:
            log = getLogger('Rkive.Tagger')
            log.fatal("Type not supported")
        except FileNotFound as e:
            log = getLogger('Rkive.Tagger')
            log.fatal("Type not supported")

    def print_file_tags(self, root, fn):
        log = getLogger('Rkive')
        fp = os.path.join(root, fn)
        log.info("Music Attributes for {0}".format(fp))
        m = MusicFile()
        m.set_filename(fp)
        m.pprint()

    def search_and_print_folder(self):
        log = getLogger('Rkive')
        log.info("print tags of music files in {0}".format(self.base))        
        visit_files(
            folder=self.base, 
            funcs=[self.print_file_tags], 
            include=self.include, 
            recursive=self.recursive)

    def search_and_modify_gain(self):
        visit_files(
            folder=self.base, 
            funcs=[self.modify_gain], 
            include=self.include)

    def modify_gain(self, root, filename):
        log = getLogger('Rkive.MusicFiles')
        cmd = ['metaflac','--add-replay-gain', filename]
        if filename.endswith('.mp3'):
            cmd = ['mp3gain', '-r', filename]
        subprocess.call(cmd, cwd=root)

    # assume that one pattern matches all the files under examination
    def modify_from_pattern(self):
        log = getLogger('Rkive.MusicFiles')        
        visit_files(
            folder=self.base, 
            funcs=[self.mod_filetags_from_regexp], 
            include=self.include)

    def mod_filetags_from_regexp(self, root, filename):
        log = getLogger('Rkive.MusicFiles')        
        (fn, ext) = os.path.splitext(filename)
        self.pattern.match(fn, self.media)
        self.modify_file_tags(root, filename)

    def modify_from_cuesheet(self):
        log = getLogger('Rkive.MusicFiles')        
        import audiotools.cue 
        import re
        cue = audiotools.cue.read_cuesheet(self.cuesheet)
        (folder, base) = os.path.split(sheet)
        if (folder ==''):
            folder = os.getcwd()
        log.info("Using cuesheet {0} in folder {1}".format(base, folder))
        os.chdir(folder)
        files = glob.glob('*.flac') 
        for filename in files:
            # shntool gives us this nice %t-%name filename
            m = re.search('(\d\d)', filename)
            if (not m):
                continue
            log.info("Setting attributes from cuesheet for file {0}".format(filename))
            tracknumber = int(m.group(0))
            # build the tag list
            # standard tags
            album_fields = cue.get_metadata().filled_fields()
            m = MusicFile()
            for a in album_fields:
                m.set_attr(a[0], a[1])
            # tags unique to track
            for f in cue.track(tracknumber).get_metadata().filled_fields():
                m.set_attr(f[0], f[1])
            m.set_attr('tracknumber', str(tracknumber))
            m.set_attr('filename', os.path.join(folder, filename))
            m.save()

    def modify_from_markup(self):
        log = getLogger('Rkive.MusicFiles')        
        tree = ET.parse(self.markup)
        albums = tree.getroot()
        for album in albums:
            for track in album:
                m = MusicFile()
                for attr in track:
                    m.set_attr(attr.tag, attr.text)
                m.save()

    def modify_file_tags(self, root, filename):
        log = getLogger('Rkive')
        fp = os.path.join(root, filename)
        if self.dryrun:
            log.info("Dryrun: Proposed tags to modify on file {0}".format(fp))
            for t,v in self.media.__dict__.items():
                log.info("Tag to set: {0} Value: {1}".format(t.encode('utf-8'), v.encode('utf-8')))
            return
        log.info("modifying tags of file {0}".format(fp))
        try:
            self.media.set_attr('filename', os.path.join(root, filename))
            self.media.save()
        except TypeNotSupported:
            log.warn("Type {0} not supported".format(fp))
            return
        except AttributeError as e:
            log.warn("Attribute error {0} with {1}".format(e, fp))
            return
       
    def search_and_modify_files(self):
        log = getLogger('Rkive')
        log.info("modify tags of music files in {0}".format(self.base))        
        visit_files(
            folder=self.base, 
            funcs=[self.modify_file_tags], 
            include=self.include, 
            recursive=self.recursive)
  
    def include(self, root, fn):
        log = getLogger('Rkive.MusicFiles')        
        basename, ext = os.path.splitext(fn)
        if ext in ['.mp3','.flac']:
            return True
        return False

if __name__ == '__main__':
    Tagger().run()
