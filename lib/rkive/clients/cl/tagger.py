import os.path
import argparse
from logging import getLogger
import glob
import re
from rkive.index.musicfile import MusicFile, Media, TypeNotSupported, FileNotFound
from rkive.clients.cl.opts import GetOpts, BaseAction, FileValidation
import rkive.clients.files
import rkive.clients.log


class ParsePattern(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(ParsePattern, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

class Tagger(object):

    def run(self, log=None):
        try:
            self.recursive = False
            go = GetOpts(parent=self)
            go.p.add_argument('--printtags', help="print files in current folder", action='store_true')
            go.p.add_argument('--file',  type=str, help="file to print out", action=FileValidation)
            go.p.add_argument('--base', type=str, help="folder in which look for files", action=BaseAction)
            go.p.add_argument('--recursive', help='used in conjunction with folder', action='store_true')
            go.p.add_argument('--tokens', type=str, help="regex for matching patterns in filenames", action=ParsePattern)
            go.p.add_argument('--cue-index', type=str, help="give a cue file for entering metadata", action=FileValidation)
            go.p.add_argument('--json-index', type=str, help="give a json file for entering metadata", action=FileValidation)
            tags = Media.TagMap
            for t,v in tags.iteritems():
                option = '--'+t
                comment = v['comment']
                go.p.add_argument(option, help=comment, type=str)
            go.get_opts()
            self.console = True
            rkive.clients.log.LogInit().set_logging(location=log, filename='tagger.log', debug=self.debug, console=self.console)
            log = getLogger('Rkive.Tagger')
            if not self.base:
                self.base = '.'
            if self.printtags:
                if self.file:
                    self.print_file_tags(self.file)
                    return
                if self.base:
                    self.search_and_print_folder()
                    return
                self.search_and_print_folder()
                return
            if self.cue_index:
                self.modify_from_cuesheet(self.cue_index)
                return
            if self.json_index:
                self.modify_from_json(self.json_index)
                return
            if self.tokens:
                self.modify_from_tokens(self.tokens)
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
                self.modify_file_tags(self.file)
                return
            if (self.base):
                self.search_and_modify_files()
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

    def print_file_tags(self, fp):
        log = getLogger('Rkive')
        try:
            m = MusicFile(fp)
            log.info("report filetags for {0}".format(fp))
            m.pprint()
        except TypeNotSupported:
            log.debug("Type {0} not supported".format(fp))
            return
   
    def search_and_print_folder(self):
        log = getLogger('Rkive')
        log.info("print tags of music files in {0}".format(self.base))        
        self.visit_files(folder=self.base, funcs=[self.print_file_tags])

    def modify_from_tokens(self, tokens):
        token_examplars = [
            '%track%', 
            '%title%',
            '%discnumber%'
            ]
        expr = ''
        self.token_index = []
        token_count = 0
        token_regexp = tokens
        for token in token_examplars:
            if token in tokens:
                token_regexp.replace(token, '(.*?)')
                tl = len(token) -2
                self.token_index.append(token[1:tl])
        self.token_regexp = re.compile(token_regexp)
        self.visit_files(folder=self.base, funcs=[self.mod_file_tags])

    def mod_filetags_from_regexp(self, fp):
        log = getLogger('Rkive.MusicFiles')        
        basename = os.path.basename(fp)
        if (not '.mp3' in basename or not '.flac' in basename):
            log.warn("Not processing {0}".format(fp))
            return
        matches = self.token_regexp.match(basename)
        if matches.groups < 1:
            log.warn("no matches in {0} for pattern {1}".format(basename,self.token_regexp))
            return
        i = 0
        for match in matches.groups:
            attr_name = self.token_index[i]
            attr_val = match
            setattr(self, attr_name, attr_val)
            i = i + 1
        self.modify_file_tags(fp)

    def modify_from_cuesheet(self, sheet):
        log = getLogger('Rkive.MusicFiles')        
        import audiotools.cue 
        import re
        cue = audiotools.cue.read_cuesheet(sheet)
        (folder, base) = os.path.split(sheet)
        if (folder ==''):
            folder = os.getcwd()
        log.info("Using cuesheet {0} in folder {1}".format(base, folder))
        os.chdir(folder)
        files = glob.glob('*.flac') 
        log.info("modify from cue sheet")
        for filename in files:
            # shntool gives us this nice %t-%name filename
            m = re.search('(\d\d)', filename)
            if (not m):
                continue
            log.info("Setting attributes from cuesheet for file {0}".format(filename))
            tracknumber = int(m.group(0))
            # build the tag list
            tags = {}
            # standard tags
            album_fields = cue.get_metadata().filled_fields()
            for a in album_fields:
                tags[a[0]] = a[1]
            # tags unique to track
            for f in cue.track(tracknumber).get_metadata().filled_fields():
                tags[f[0]] = f[1]
            log.info("Found these attributes from cuesheet")
            for t,v in tags.iteritems():
                log.info("{0}: {1}".format(t.encode('utf-8'),v.encode('utf-8')))
            # direct map from cuesheet to standard tags
            if not 'artist_name' in tags:
                tags['artist'] = tags['performer_name'] 
            if not 'track_number' in tags:
                tags['tracknumber'] = str(tracknumber)
            # now map from cuesheet tags to standard via the CueMap
            for t,v in Media.CueMap.iteritems():
                if (t in tags):
                    tags[v] = tags[t]
                    del tags[t]
            # set the file
            fp = os.path.join(folder, filename)
            m = MusicFile(fp)
            m.set_tags_from_list(tags)
            m.save()
            log.info("======================================")

    def modify_from_json(self, sheet):
        log = getLogger('Rkive.MusicFiles')        
        json = self.load_json(sheet)
        for record in json:
            # build the tag list
            filename = record['filename']
            del record['filename']
            # set the file
            fp = os.path.join(self.base, filename)
            log.info("modify: {0}".format(fp))
            m = MusicFile(fp)
            m.set_tags_from_list(record)
            m.save()
            log.info("======================================")
    
    def load_json(self, f):
        import json
        fh = open(f)
        return json.load(fh)

    def modify_file_tags(self, fp):
        log = getLogger('Rkive')
        log.info("modifying tags of file {0}".format(fp))
        try:
            m = MusicFile(fp)
            m.set_tags(self)
            m.save()
        except TypeNotSupported:
            log.debug("Type {0} not supported".format(fp))
            return
        except AttributeError as e:
            log.warn("Attribute error {0} with {1}".format(e, fp))
            return
       
    def search_and_modify_files(self):
        log = getLogger('Rkive')
        log.info("print tags of music files in {0}".format(self.base))        
        self.visit_files(folder=self.base, funcs=[self.modify_file_tags])
   
    def visit_files(self, folder='', funcs=[]):
        files = os.listdir(folder)
        for f in files:
            if (f.startswith('.')):
                next
            fp = os.path.join(folder, f)
            if (self.recursive):
                if (os.path.isdir(fp)):
                    self.visit_files(folder=fp, funcs=funcs)
            for func in funcs:
                func(fp)

if __name__ == '__main__':
    Tagger().run()
