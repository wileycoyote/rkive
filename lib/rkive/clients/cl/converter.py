# allowed types
import os
import subprocess
import sys
import argparse
from logging import getLogger
import glob
import copy
from rkive.clients.cl.opts import GetOpts
import rkive.clients.cl.opts
from rkive.clients.files import visit_files
import rkive.clients.log

class ConvertClient(object):
    split_cmd = ['cuebreakpoints','"[cuefile]"', '|', 'shnsplit', '-O', 'always', '-o', '[type]', '"[infile]"'],    
    ffmpeg_mp3 =  ['ffmpeg', '-i', '"[infile]"', '-acodec','libmp3lame', '-ab', '128k', '-map_metadata 0:s:0','"[outfile]"']
    convert_cmd = {
        '.ogg' : ffmpeg_mp3,
        '.wav' : ['pacpl', '-t', 'flac', '[infile]'],
        '.m4a' : ffmpeg_mp3
    }
    def run(self, logloc=""):
        base = '.'
        try:
            go = rkive.clients.cl.opts.GetOpts(parent=self)
            go.p.add_argument(
                '--convert',  
                help="", 
                action='store_true')
            go.p.add_argument(
                '--split',
                nargs=1,
                help="name of cue file to be split",
                action=FileValidation)
            go.get_opts()
            rkive.clients.log.LogInit().set_logging(location=logloc, filename='converter.log', debug=self.debug, console=self.console)
            log = getLogger('Rkive.Converter')
            if self.convert:
                visit_files(folder=self.base, funcs=[self.convert_file], include=self.include_convert)
                sys.exit()
            if self.split:
                visit_files(folder=self.base, funcs=[self.split_file], include=self.include_split)
                sys.exit()
        except SystemExit:
            pass
    
    def include_convert(self, root, fn):
        base, ext = os.path.splitext(fn)
        if ext in ['.wav', '.ogg', '.m4a']:
            return True
        return False

    def include_split(self, root, fn):
        base, ext = os.path.splitext(fn)
        if ext in ['.cue']:
            return True
        return False

    def split_file(self, root, filename):
        log = getLogger('Rkive.Converter')
        fp = os.path.join(root, filename)
        path, cuefn = os.path.split(fp)
        cue,ext = os.path.splitext(cuefn)
        file_to_split = glob.glob(cue+'.*')
        cmd = copy.copy(self.split_cmd)[0]
        print file_to_split
        cmd[1] = cmd[1].replace('[cuefile]',cuefn)
        cmd[7] = cmd[7].replace('[type]', 'flac')
        cmd[8] = cmd[8].replace('[infile]', file_to_split[0])
        if self.dryrun:
            c = ' '.join(cmd)
            log.info("Command line to use for split {0}".format(c))
            return
        c = ' '.join(cmd)
        o = subprocess.check_output(c,cwd=root, shell=True)
        print o

    def convert_file(self, root, filename):
        log = getLogger('Rkive')
        base,ext = os.path.splitext(filename)
        cmd = copy.copy(self.convert_cmd[ext])
        cmd[-1] = cmd[-1].replace('[infile]', filename)
        #cmd[-2] = cmd[-2].replace('[outfile]',base)
        if self.dryrun:
            c = ' '.join(cmd)
            log.info("Command line to use for convert {0}".format(c))
            return
        c = ' '.join(cmd)
        log.info("Command line to use for convert {0}".format(c))
        subprocess.call(cmd, cwd=root)

