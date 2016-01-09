# -*- coding: utf-8 -*-
from logging import getLogger
import os.path
import audiotools.cue 
import json

class cue2json(object):
    
    def run(self, cue_sheet):
        log = getLogger('Rkive.Index')
        if (not os.path.exists(cue_sheet)):
            log.fatal("file {0} does not exist".format(cue))
            return None        
        cue = mycue.read_cuesheet(cue_sheet)
        files = getattr(cue, '__files__')
        jrec = {'files' : {}}
        for f in files:
            filename = f.filename()
            jrec.files[filename] = {}
            tracks = getattr(f, '__tracks__') 
            for t in tracks:
                title = getattr(t,'__title__')
                track = t.number()
                artist = getattr(t,'__performer__')
                jrec.files[filename]['title'] = title
                jrec.files[filename]['track'] = track
                jrec.files[filename]['artist'] = artist
        return jrec

class json2flac(object):

    def run(self, json):
        pass        
