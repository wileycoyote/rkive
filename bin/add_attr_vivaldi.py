#!/usr/bin/env python
from rkive.index.musicfile import MusicFile
import os.path
import os
import re
root = '/home/roger/Projects/Antonio Vivaldi - The Masterworks (Box Set) [2004]'
data = os.path.join(root, 'data')
composer = 'Vivaldi'
grouping = 'Antonio Vivaldi - The Masterworks [Brillian, 2004]'
artists = {}
with open('data') as fh:
    for l in fh:
        l = l.strip()
        cd, artists = l.split(',')
        artists[cd] = artists
dirs = os.listdir(root)
exclude = [
    'data',
    'folder.jpg',
    'images'
]
for d in dirs:
    if d in exclude:
        continue
    pre, album_title = d.split(' - ', 1) 
    cd_number = re.match('^The Masterworks \(CD (\d\d)\)', pre)
    print(cd_number.group(1))
    print(album_title)
    continue

    cdroot = os.path.join(root, l[2:]) 
    files = os.listdir(cdroot)
    
    for f in files:
        if not f.endswith('.flac'):
            continue
        fp = os.path.join(cdroot, f)
        print("Modifying {0}".format(fp))
        mf = MusicFile()
        setattr(mf, 'album', album_title)
        setattr(mf, 'composer', composer)
        setattr(mf, 'genre', 'Baroque')
        setattr(mf, 'discnumber',cd_number)
        setattr(mf, 'filename', fp)
        setattr(mf, 'grouping', grouping)
        mf.save()


