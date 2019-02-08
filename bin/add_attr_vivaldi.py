#!/usr/bin/env python
from rkive.index.musicfile import MusicFile
import os.path
import os
import re
root = (
    '/home/roger/Projects/Antonio Vivaldi '
    '- The Masterworks (Box Set) [2004]'
)
data = os.path.join(root, 'data')
composer = 'Vivaldi'
grouping = 'Antonio Vivaldi - The Masterworks [Brillian, 2004]'
artists = {}
with open('data') as fh:
    for x in fh:
        x = x.strip()
        cd, artists = x.split(',')
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
    cd_number = re.match(r'^The Masterworks \(CD (\d\d)\)', pre)

    cdroot = os.path.join(root, d)
    if not os.path.exists(cdroot):
        print(f"path {cdroot} does not exist")
        continue
    files = os.listdir(cdroot)

    for f in files:
        if not f.endswith('.flac'):
            continue
        fp = os.path.join(cdroot, f)
        print("Modifying {0}".format(fp))
        mf = MusicFile()
        mf.media = fp
        mf.album = album_title
        mf.composer = composer
        mf.genre = 'Baroque'
        mf.discnumber = cd_number
        mf.grouping = grouping
        mf.save()
