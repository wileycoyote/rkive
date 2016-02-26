import os.path
import argparse
from logging import getLogger
import glob
import re
from rkive.index.musicfile import MusicFile, Media, TypeNotSupported, FileNotFound
from rkive.clients.cl.opts import GetOpts, BaseAction, FileValidation
import rkive.clients.regexp
from rkive.clients.files import visit_files
import rkive.clients.log
import subprocess

class ParsePattern(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(ParsePattern, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

class Tagger(object):

    def run(self, logloc=None):
        try:
            self.recursive = False
            self.base = '.'
            self.debug = False
            go = GetOpts(parent=self)
            go.p.add_argument('--printtags', help="print files in current folder", action='store_true')
            go.p.add_argument('--file',  type=str, help="file to print out", action=FileValidation)
            go.p.add_argument('--base', type=str, help="folder in which look for files", action=BaseAction)
            go.p.add_argument('--recursive', help='used in conjunction with folder', action='store_true')
            go.p.add_argument('--pattern', type=str, help="regex for matching patterns in filenames", action=ParsePattern)
            go.p.add_argument('--cuesheet', type=str, help="give a cue file for entering metadata", action=FileValidation)
            go.p.add_argument('--markdown', type=str, help="give file containing metadata", action=FileValidation)
            go.p.add_argument('--gain', help="add gain to music files", action='store_true')
            tags = Media.TagMap
            for t,v in tags.iteritems():
                option = '--'+t
                comment = v['comment']
                go.p.add_argument(option, help=comment, type=str)
            go.get_opts()
            self.console = True
            rkive.clients.log.LogInit().set_logging(location=logloc, filename='tagger.log', debug=self.debug, console=self.console)
            log = getLogger('Rkive.Tagger')
            if self.printtags:
                if self.file:
                    folder, filename = os.path.split(self.file)
                    self.print_file_tags(folder, filename)
                    return
                if self.base:
                    self.search_and_print_folder()
                    return
                self.search_and_print_folder()
                return
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
            # check arguments for something to add tags/to
            hasargs = False
            for t,v in tags.iteritems():
                if (getattr(self, t)):
                    hasargs = True
                    break
            if (not hasargs):
                log.info("no attributes to apply")
                return
            if (self.file):
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
        try:
            m = MusicFile(fp)
            log.info("report filetags for {0}".format(fp))
            m.pprint()
        except TypeNotSupported:
            log.warn("Type {0} not supported".format(fp))
            return
   
    def search_and_print_folder(self):
        log = getLogger('Rkive')
        log.info("print tags of music files in {0}".format(self.base))        
        visit_files(folder=self.base, funcs=[self.print_file_tags], include=self.include)

    def search_and_modify_gain(self):
        visit_files(folder=self.base, funcs=[self.modify_gain], include=self.include)

    def modify_gain(self, root, filename):
        log = getLogger('Rkive.MusicFiles')
        cmd = ['metaflac','--add-replaygain', 'filename']
        if filename.endswith('.mp3'):
            cmd = ['mp3gain', '-r', 'filename']
        subprocess.call(cmd, cwd=root)

    # assume that one pattern matches all the files under examination
    def modify_from_pattern(self):
        log = getLogger('Rkive.MusicFiles')        
        self.tx_pattern = rkive.clients.regexp.Regexp(self.pattern)
        visit_files(folder=self.base, funcs=[self.mod_filetags_from_regexp], include=self.include)

    def mod_filetags_from_regexp(self, root, filename):
        log = getLogger('Rkive.MusicFiles')        
        (fn, ext) = os.path.splitext(filename)
        self.tx_pattern.match(fn, self)
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
            self.clear_tag_attrs()
            for a in album_fields:
                self.set_tag_attr(self, a[0], a[1])
            # tags unique to track
            for f in cue.track(tracknumber).get_metadata().filled_fields():
                self.set_tag_attr(self, f[0], f[1])
            self.set_tag_attr(self, 'tracknumber', str(tracknumber))
            self.modify_file_tags(folder, filename)

    def modify_from_markdown(self):
        log = getLogger('Rkive.MusicFiles')        
        with open(self.markdown) as m:
            header = m.readline().strip().split(',')
            nrrecords = header.pop(0)
            recordlen = int(header.pop(0))
            line_counter = 0
            record = []
            for l in m:
                line_counter = line_counter + 1
                record.append(l.strip())
                if line_counter%recordlen == 0:
                    reccnt = 0
                    filename = ''
                    log.debug("size of array: {0}".format(len(record)))
                    for val in record:
                        log.debug("reccnt {0}".format(reccnt))
                        name = header[reccnt]
                        if name == 'filename':
                            filename = val
                        else:
                            log.info("name: {0} val: {1}".format(name, val))
                            self.set_tag_attr(name, val)
                        reccnt = reccnt + 1
                    if filename:
                        fp = os.path.join(self.base, filename)
                        self.modify_file_tags(fp)
                    else:
                        log.fatal("No filename to save tags")
                    record = []

    def clear_tag_attrs(self):
        for t,v in Media.TagMap.iteritems():
            setattr(self, t, "")

    def set_tag_attr(self, name, val):
        log = getLogger('Rkive')
        if name in Media.TagMap:
            log.debug("{0}: {1}".format(name,val))
            setattr(self, name, val)
            return True
        log.warn("Not setting tag {0} for value {1}".format(name,val))
        return False

    def modify_file_tags(self, root, filename):
        log = getLogger('Rkive')
        fp = os.path.join(root, filename)
        if self.dryrun:
            log.info("Dryrun: Proposed tags to modify on file {0}".format(fp))
            for t,v in Media.TagMap.iteritems():
                v = getattr(self, t)
                log.debug("t {0} v {1}".format(t,v))
                if v:
                    log.info("Tag to set: {0} Value: {1}".format(t.encode('utf-8'), v.encode('utf-8')))
            return
        log.info("modifying tags of file {0}".format(fp))
        try:
            m = MusicFile(fp)
            m.set_tags(self)
            m.save()
        except TypeNotSupported:
            log.warn("Type {0} not supported".format(fp))
            return
        except AttributeError as e:
            log.warn("Attribute error {0} with {1}".format(e, fp))
            return
       
    def search_and_modify_files(self):
        log = getLogger('Rkive')
        log.info("modify tags of music files in {0}".format(self.base))        
        visit_files(folder=self.base, funcs=[self.modify_file_tags], include=self.include)
  
    def include(self, root, fn):
        log = getLogger('Rkive.MusicFiles')        
        basename, ext = os.path.splitext(fn)
        if ext in ['.mp3','.flac']:
            return True
        return False

if __name__ == '__main__':
    Tagger().run()
