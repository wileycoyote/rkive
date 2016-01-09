#!/usr/bin/env python
import clients.files
from musicfile import MusicFile

def process_title(fp):
    title = ''
    try:
    	m = MusicFile()
       	m.set_media(fp)
        e = fp.split('/')[1]
        title = 'Bach - Hanssler '+e[0:6]+ ' - '+e[10:]
        nt = {}
        nt['album'] = title
        m.set_tags_from_list(nt)
        m.save()
        return
    except Exception as e:
        print fp
        print "PROBLEMi "+str(e)
        return
base = '.'

clients.files.visit(base='.', func=[process_title])

