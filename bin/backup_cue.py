#!/usr/bin/env python
import os
import glob
import re
def rename_files(files, src, tgt):
    for f in files:
        src_f = '/'.join([src, f])
        tgt_f = '/'.join([tgt, f])
        print "rename {0} to {1}".format(src_f, tgt_f)
        os.rename(src_f, tgt_f)    

with open('data/files_split_karn.txt', 'r') as fh:
    for l in fh.readlines():
        if l.startswith('#'): 
            continue
        srcdir = l.strip().split("\t")[1]
        tgtdir = '/media/Backup/'+'_'.join(srcdir.split('/')[3:-1])
        if (not os.path.exists(tgtdir)):
            print "Making "+tgtdir
            os.mkdir(tgtdir)
        os.chdir(srcdir)
        print "change to {0}".format(srcdir)
        cues = glob.glob('*.cue')
        rename_files(cues, srcdir, tgtdir)
        flacs = glob.glob('*.flac')
        r = re.compile('^\d\d')
        files = []
        for flac in flacs:
            if (not r.match(flac)):
                files.append(flac)
        rename_files(files, srcdir, tgtdir)
        apes = glob.glob('*.ape')
        rename_files(apes, srcdir, tgtdir)
	
