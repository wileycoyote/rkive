#!/usr/bin/env python
from rkive.index.musicfile import MusicFile
import os.path
import os
root='/media/roger/Music/Collections/Various/Mozart - Complete Works [Phillips]'
title_prefix = 'Complete Mozart [Phillips], '
with open('data/mozart_cds') as fh:
    for l in fh:
        l=l.strip()
        (dot, title,cd) = l.split('/')
        full_title = title_prefix+title 
        cd_number = str(int(cd[2:]))
        print("title: {0} cd: {1} cdnumber: {2}".format(title, cd, cd_number))
        cdroot = os.path.join(root, l[2:]) 
        files=os.listdir(cdroot)
        for f in files:
            if not f.endswith('.mp3'):
                continue
            fp = os.path.join(cdroot, f)
            print("Modifying {0}".format(fp))
            mf = MusicFile()
            setattr(mf, 'album', full_title)
            setattr(mf, 'discnumber',cd_number)
            setattr(mf, 'filename', fp)
            mf.save()


