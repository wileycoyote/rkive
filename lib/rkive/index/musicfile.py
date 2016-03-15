# -*- coding: utf-8 -*-
import os.path
from logging import getLogger
from mutagen.id3 import ID3
from mutagen.id3 import error as id3_error
from mutagen.flac import FLAC, Picture
from mutagen.id3 import TIT1, TIT2, TPE2, TALB, TPE1, TDAT, TRCK, TCON, TORY, TPUB, TDRC, TPOS, COMM, TCOM, APIC
from PIL import Image
import weakref

class InvalidTag(Exception): pass

class Media(object):

    CueMap = {
        'album_name' : 'album',
        'performer_name' : 'albumartist',
        'track_number' : 'tracknumber',
        'track_name' : 'title'
    }

    TagMap = {
        'grouping' : {
            'flac' : ['grouping'],
            'mp3' : ['TIT1', TIT1],
            'comment' : 'Grouping'
        },
        'album'    : {
            'flac' : ['album'],
            'mp3' : ['TALB', TALB],
            'comment' : 'Album Name'
        },
        'albumartist' : {
            'flac' : ['albumartist'],
            'mp3' : ['TPE2', TPE2],
            'comment' : 'Album artist set to "Various Artists" for multiple artists'
        },
        'artist'      : {
            'flac' : ['artist'],
            'mp3' : ['TPE1', TPE1],
            'comment' : 'Artist, seperate by ; if multiple'
        },
        'comment'     : {
            'flac' : ['comment'],
            'mp3' : ['COMM', COMM],
            'comment' : 'Comment'
        },
        'composer'    : {
            'flac' : ['composer'],
            'mp3' : ['TCOM', TCOM],
            'comment' : 'composer'
        },
        'discnumber'  : {
            'flac' : ['discnumber'],
            'mp3' : ['TPOS', TPOS],
            'comment' : 'disc number',
            'default' : 1
        },
        'disctotal'   : {
            'flac' : ['disctotal'],
            'default' : 1,
            'mp3' : ['TPOS', TPOS],
            'comment' : 'Number of discs'
        },
        'genre'       : {
            'flac' : ['genre'],
            'mp3' : ['TCON',TCON],
            'comment' : 'Only one genre'
        },
        'picture'     : {
            'mp3' : ['APIC', APIC],
            'flac' : ['picture'],
            'comment' : 'The filename for a image associated with file'
        },
        'title'       : {
            'flac' : ['title'],
            'mp3' : ['TIT2', TIT2],
            'comment' : 'title'
        },
        'tracknumber' : {
            'flac' : ['tracknumber'],
            'mp3' : ['TRCK', TRCK],
            'comment' : 'tracknumber - start from 1'
        },
        'tracktotal'  : {
            'default' : 1,
            'comment' : 'total number of tracks'
        },
        'year'        : {
            'flac' : ['year'],
            'mp3' : ['TDRC', TDRC],
            'comment' : 'Year of original recording, remaster dates go in comment'
        },
    } 

    def get_class(self):
        log = getLogger('Rkive.MusicFile')
        log.warn("Class object not instanciated")
        return None

    def save(self):
        log = getLogger('Rkive.MusicFile')
        log.warn("Save method not instanciated")
        return None

class MP3(Media):
  
    def __init__(self):
        self.t = 'mp3'

    def get_class(self):
        try:
            mp3 = ID3(self.filename)
            return mp3
        except id3_error:
            mp3 = ID3()
            mp3.save(self.filename)
            return mp3

    def save(self):
        log = getLogger('Rkive.MusicFile')
        log.info("save file {0}".format(self.filename))
        id3 = self.get_class()
        discnumber = None
        disctotal = None
        if (hasattr(self, 'discnumber')):
            discnumber = getattr(self, 'discnumber') 
        if (hasattr(self, 'disctotal')):
            disctotal = getattr(self, 'disctotal')
        v = None
        k, f = self.TagMap['discnumber']['mp3']
        if hasattr(id3, k):
            c = id3[k]
            id3.delall(k)
            if ('/' in c):
                dn, dt = '/'.split(c)
                if (discnumber):
                    dn = discnumber
                if (disctotal):
                    dt = disctotal
                v = dn+'/'+dt
            else:
                dn = c
                if (discnumber):
                    v = discnumber
                else:
                    v = dn
                if (disctotal):
                    v = v+'/'+disctotal
        else:
            if (discnumber):
                v = discnumber
            if (disctotal):
                if (not discnumber):
                    v = '1'
                v = v+'/'+disctotal
        if (v):
            id3.add(f(encoding=1, text=unicode(v)))
        for t in self.TagMap:
            if t == 'discnumber':
                continue
            if t == 'disctotal':
                continue
            if (not hasattr(self, t)):
                continue
            v = getattr(self, t)
            log.debug("loop through tag values")
            if (v):
                key, func = self.TagMap[t]['mp3']
                log.debug("modifying tag {0} with value {1} ".format(key, v))
                id3.delall(key)
                id3.add(func(encoding=3, text=unicode(v.decode('utf-8'))))
        id3.save()

class Flac(Media):
   
    def get_class(self):
        try:
            return FLAC(self.filename)
        except mutagen.flac.error:
            flac = FLAC()
            flac.save(self.filename)
            return flac

    def save(self):
        log = getLogger('Rkive.MusicFile')
        log.info("save file {0}".format(self.filename))
        flac = self.get_class()
        if hasattr(self,'picture'):
            flac.clear_pictures()
            pic = Picture()
            with open(self.picture, "rb") as f:
                pic.data = f.read()
            im = Image.open(self.picture)
            pic.type = 3
            if v.endswith('jpg'):
                pic.mime = u"image/jpeg"
            if v.endswith('png'):
                pic.mime = u"image/png"
            pic.width = im.size[0] 
            pic.height = im.size[1]
            flac.add_picture(pic)
            delattr(self, 'picture')
        for t in self.TagMap:
            if hasattr(self, t):
                v = getattr(self, t)
                log.debug("{0}: {1}".format(t,v))
                if v:
                    log.debug("{0}: {1}".format(t, v))
                    v = v.encode('utf-8')
                    flac[t] = v.decode('utf-8')
        flac.save()

class FileNotFound(Exception):
    pass

class TypeNotSupported(Exception):
    pass
#
# Proxy Object

class MusicFile(object):

    Types = {
        'mp3'  : MP3,
        'flac' : Flac
    } 
    g = lambda x: getattr(x.media,'filename')
    s = lambda x,y: setattr(x.media, 'filename', y)
    d = lambda x: delattr(x.media, 'filename')
    filename=property(g,s,d,'filename')

    def __init__(self, filename):
        log = getLogger('Rkive.MusicFile')
        log.info("Filename: {0}".format(filename))
        if (not os.path.exists(filename)):
            log.warn("Path not found {0}".format(filename))
            raise FileNotFound
        self.mediatype = filename.rsplit('.', 1)[1]
        if (not self.mediatype in self.Types):
            raise TypeNotSupported 
        if ('.AppleDouble' in filename):
            raise TypeNotSupported
        self.media = self.Types[self.mediatype]()
        self.filename = filename

    def set_tags_from_list(self, l):
        log = getLogger('Rkive.MusicFiles')
        log.info("Setting attributes from list for {0}".format(self.media.filename))
        for t,v in l.items():
            if (t in Media.TagMap):
                log.info("{0}: {1}".format(t.encode('utf-8'),v.encode('utf-8')))
                setattr(self, t, v)

    def print_attr(self):
        log = getLogger('Rkive.MusicFiles')
        for m in Media.TagMap:
            v = getattr(self, m)
            if v:
                log.info("Tag: {0} Value: {1}".format(m, v))

    def pprint(self):
        c = self.media.get_class()
        print(c.pprint())

    def save(self):
        self.media.save()

for t,v in Media.TagMap.items():
    print(t)
    #g = lambda x,y='': getattr(x.media,Media.TagMap[y][x.mediatype][0]) if y else None
    g = lambda x: getattr(x.media, 'album')
    s = lambda x,y: setattr(x.media,'album', y)
    d = lambda x: delattr(x.media, t) 
    setattr(MusicFile, t, property(g,s,d))

