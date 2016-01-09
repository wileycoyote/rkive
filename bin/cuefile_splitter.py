#!/usr/bin/env python
from rkive.clients.cl.tagger import Tagger
from logging import getLogger
import os
import os.path
import sys
import subprocess
import glob
import audiotools.cue
import argparse
import datetime
from logging import getLogger

def visit_files(data, func):
    log = getLogger('Rkive.Splitter')
    log.info("read {0}".format(data))
    with open(data) as f:
        for l in f.readlines():
            l = l.strip()
            if (l.startswith('#')):
                continue
            (local_working_folder, remote_working_folder) = l.split("\t")
            if (not os.path.exists(local_working_folder)):
                os.makedirs(local_working_folder)
            os.chdir(local_working_folder)
            func(local_working_folder, remote_working_folder)

class Splitter(object):

    media = [
        'flac',
        'ape',
        'cue'
    ]

    def split_file(self, cue, media):
        log = getLogger('Rkive.Splitter')
        # split
        shntool = [
            '/opt/local/bin/shnsplit', 
            '-O',
            'always',
            '-o', 
            'flac', 
            '-t', 
            '%n-track', 
            '-f', 
        ]
        shntool.append(cue)
        shntool.append(media)
        log.info("shntool cmd: {0}".format(' '.join(shntool)))
        output = subprocess.check_call(shntool,stderr=subprocess.STDOUT)
        log.info("output from splitter: {0}".format(output))

    def valid_media(self, o):
        for m in self.media:
            if (o.endswith(m)):
                return True
        return False
 
    def split(self, local_working_folder):
        log = getLogger('Rkive.Splitter')
        cue_files = glob.glob('*.cue')
        media_files = glob.glob('*.flac')
        if (not media_files):
            media_files = glob.glob('*.ape')
        if (not media_files):
            log.fatal("No media folders in {0}".format(local_working_folder))
            return
        for c in cue_files:
            log.info("working with cue file {0}".format(c))
            found_media = None
            (dummy, cue_base) = os.path.split(c)
            cue_base = cue_base.split('.', 1)[0]
            for m in media_files:
                b = m.split('.', 1)[0]
                if (b == cue_base):
                    found_media = os.path.join(local_working_folder, m)
                    break
            self.split_file(c, found_media)

    def tag(self, l, r):
        log = getLogger('Rkive.Splitter')
        # tag
        cue_files = glob.glob('*.cue')
        for cue in cue_files:
            t = Tagger()
            cue = os.path.join(l, cue)
            log.info("Using cuesheet: {0}".format(cue))
            t.modify_from_cuesheet(cue)

if __name__ == '__main__':
    clients.log.LogInit().set_logging(filename='logs/splitter.log', debug=True, console=True)
    log = getLogger('Rkive.Splitter')
    Splitter.split('.')
