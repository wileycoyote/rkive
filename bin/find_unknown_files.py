#!/usr/bin/python

from rkive.clients.files import visit

known_files = [
    'mp3',
    'flac',
    'jpg',
    'jpeg',
    'txt',
    'log',
    'png',
    'gif',
    'cue',
    'm3u',
    'doc',
    'htm',
    'info',
    'nfo',
    'pdf',
    'md5',
    'm3u8',
    'tif',
    'rtf',
    'djvu',
    'bmp'
]
def store_unknown_files(fp):
    known_cnt = 0
    ffp = fp.lower()
    for k in known_files:
        if (not ffp.endswith(k)):
            known_cnt = known_cnt +1
    if (known_cnt == len(known_files)):
        print "unknown file: "+fp
root='/media/azure/Multimedia/Music'
visit(base=root,func=[store_unknown_files])
