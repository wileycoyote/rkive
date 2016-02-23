# allowed types
import os
import subprocess
import sys
import argparse

import rkive.clients.cl.opts

class ConverterClient(object):
    split = ['cuebreakpoints','"[cuefile]"', '|', 'shnsplit', '-O', 'always', '-o', '[type]', '"[infile]"'],    
    ffmpeg_mp3 =  ['ffmpeg', '-i', '"[infile]"', '-acodec','libmp3lame', '-ab', '128k', '-map_metadata 0:s:0','"[outfile]"']
    convert = {
            'ogg' : ffmpeg_mp3,
            'wav' : ['pacpl', '-i', '"[infile]"', '-t', 'flac', '--outfile','"[outfile]"'],
            'm4a' : ffmpeg_mp3
            }
    def run(self):
        base = '.'
        try:
            self.recursive = False
            go = rkive.clients.cl.opts.GetOpts(parent=self)
            go.p.add_argument(
                    '--base', 
                    nargs=1, 
                    help="full path to base of files", 
                    action=rkive.clients.cl.opts.BaseAction)
            go.p.add_argument(
                '--recursive', 
                help="recurse through folders", 
                action='store_true')
            go.p.add_argument(
                '--convert',  
                help="", 
                action='store_true')
            go.p.add_argument(
                '--split',
                nargs=1,
                help="name of cue file to be split",
                action=FileValidation)
            self.console = True
            rkive.clients.log.LogInit().set_logging(location=log, filename='converter.log', debug=self.debug, console=self.console)
            log = getLogger('Rkive.Tagger')
            go.get_opts()
            if self.convert:
                visit_files(folder=self.base, funcs=[self.convert_file], include=['.wav','.ogg','.m4a'])
                sys.exit()
            if self.split:
                visit_files(folder=self.base, funcs=[self.split_file], include=['.cue'])
                sys.exit()
        except SystemExit:
            pass
    
    def split_file(self, fp):
        log = getLogger('Rkive')
        path, cuefn = os.path.split(fp)
        cue,ext = os.path.splitext(cuefn)
        file_to_split = glob.glob(cue+'.*')
        self.split[1] = self.split[1].replace('[cuefile]',cuefn)
        self.split[7] = self.split[7].replace('[type]', 'flac')
        self.split[8] = self.split[8].replace('[infile]', file_to_split)
        if self.dryrun:
            c = ' '.join(self.split)
            log.info("Command line to use for split {0}".format(c))
            return
        subprocess.call(self.split)

    def convert_file(self, fp):
        log = getLogger('Rkive')
        path, fn = os.path.split(fp)
        base,ext = os.path.splitext(fn)
        self.convert[2] = self.convert[2].replace('[infile]', fp)
        outfile =os.path.join(path, base+'.flac')
        self.convert[-1] = self.convert[-1].replace('[outfile]',outfile)
        if self.dryrun:
            c = ' '.join(self.convert)
            log.info("Command line to use for convert {0}".format(c))
            return
        subprocess.call(self.convert)

