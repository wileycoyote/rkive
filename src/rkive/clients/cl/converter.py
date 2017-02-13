# allowed types
import os
import subprocess
import sys
import argparse
from logging import getLogger
import glob
import copy
from rkive.clients.cl.opts import GetOpts,FileValidation
from rkive.clients.files import visit_files
from rkive.clients.log import LogInit

class ConvertClient(GetOpts):
    split_cmd = ['cuebreakpoints','"[cuefile]"', '|', 'shnsplit', '-O', 'always', '-o', '[type]', '"[infile]"'],
    ffmpeg_mp3 =  ['ffmpeg', '-y', '-i', '[infile]', '[outfile]']
    convert_cmd = {
        '.ogg' : ffmpeg_mp3,
        '.wav' : ['pacpl', '-t', 'flac', '[infile]'],
        '.m4a' : ffmpeg_mp3,
        '.mp4' : ffmpeg_mp3,
        '.opus' : ffmpeg_mp3
    }

    def __init__(self):
        self.convert = False
        self.split = False

    def run(self):
        try:
            log = getLogger('Rkive.Converter')
            if self.convert:
                visit_files(
                    folder=self.base, 
                    funcs=[self.convert_file], 
                    include=self.include_convert,
                    recursive=self.recursive
                )
                sys.exit()
            if self.split:
                print("Folder: "+self.base)
                visit_files(
                    folder=self.base, 
                    funcs=[self.split_file], 
                    include=self.include_split)
                sys.exit()
        except SystemExit:
            pass
    
    def include_convert(self, root, fn):
        base, ext = os.path.splitext(fn)
        log = getLogger('Rkive.Converter')
        if ext in self.convert_cmd.keys():
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
        cmd[1] = cmd[1].replace('[cuefile]',cuefn)
        cmd[7] = cmd[7].replace('[type]', 'flac')
        cmd[8] = cmd[8].replace('[infile]', file_to_split[0])
        if self.dryrun:
            c = ' '.join(cmd)
            log.info("Command line to use for split {0}".format(c))
            return
        c = ' '.join(cmd)
        o = subprocess.check_output(c,cwd=root, shell=True)

    def convert_file(self, root, filename):
        log = getLogger('Rkive')
        base,ext = os.path.splitext(filename)
        cmd = copy.copy(self.convert_cmd[ext])
        cmd[3] = cmd[3].replace('[infile]', filename)
        cmd[-1] = cmd[-1].replace('[outfile]',base+'.mp3')
        log.debug("filename: {0}, base: {1}".format(filename, base))
        c = ' '.join(cmd)
        log.info("Command line to use for convert {0} #### {1} #####".format(c, root))
        if self.dryrun:
            return
        subprocess.call(cmd, cwd=root)

