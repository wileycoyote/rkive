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
            'flac' : ['tracktotal'],
            'mp3': ['tracktotal'],
            'default' : 1,
            'comment' : 'total number of tracks'
        },
        'year'        : {
            'flac' : ['year'],
            'mp3' : ['TDRC', TDRC],
            'comment' : 'Year of original recording, remaster dates go in comment'
        },
    } 

    def save(self):
        log = getLogger('Rkive.MusicFile')
        log.warn("Save method not instanciated")
        return None

class MP3(Media):
  
    def __init__(self, filename):
        self.filename = filename

    def get_object(self):
        try:
            return(ID3(self.filename))
        except id3_error:
            mp3 = ID3()
            mp3.save(self.filename)
            return mp3

    def save(self):
        log = getLogger('Rkive.MusicFile')
        log.info("save file {0}".format(self.filename))
        mp3 = self.get_object()
        discnumber = None
        disctotal = None
        if (hasattr(self, 'discnumber')):
            discnumber = getattr(self, 'discnumber') 
        if (hasattr(self, 'disctotal')):
            disctotal = getattr(self, 'disctotal')
        v = None
        t, f = self.TagMap['discnumber']['mp3']
        if hasattr(mp3, t):
            c = mp3[t]
            mp3.delall(t)
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
            if discnumber:
                delattr(self, 'discnumber')
            if disctotal:
                delattr(self, 'disctotal')
            mp3.add(f(encoding=1, text=v))
        log.debug("loop through tag values "+str(self.__dict__))
        for t,v in self.__dict__.items():
            if (not t in Media.TagMap):
                continue
            id3_key, func = self.TagMap[t]['mp3']
            log.debug("modifying tag {0} with value {1} ".format(id3_key, v))
            mp3.delall(id3_key)
            mp3.add(func(encoding=3, text=v))
        mp3.save()

class Flac(Media):

    def __init__(self, filename):
        self.filename = filename

    def get_object(self):
        try:
            return(FLAC(self.filename))
        except mutagen.flac.error:
            flac = FLAC()
            flac.save(self.filename)
            return flac

    def save(self):
        log = getLogger('Rkive.MusicFile')                
        flac = self.get_object()
        if hasattr(self, 'picture'):
            flac.clear_pictures()
            pic = Picture()
            with open(self.picture, "rb") as f:
                pic.data = f.read()
            im = Image.open(self.picture)
            pic.type = 3
            v = getattr(self, 'picture')
            if v.endswith('jpg'):
                pic.mime = u"image/jpeg"
            if v.endswith('png'):
                pic.mime = u"image/png"
            pic.width = im.size[0] 
            pic.height = im.size[1]
            flac.add_picture(pic)
            delattr(self, 'picture')
        for t,v in self.__dict__.items():
            if (not t in Media.TagMap):
                continue
            log.debug("Tag: {0}: {1}".format(t, v))
            flac[t] = v
        flac.save()

class FileNotFound(Exception):
    pass

class TypeNotSupported(Exception):
    pass

class MediaObjectNotFound(Exception):
    pass
#
# Proxy Object

class MusicFile(object):

    Types = {
        'mp3'  : MP3,
        'flac' : Flac
    } 

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
        self.media = self.Types[self.mediatype](filename)

    def set_tags_from_list(self, l):
        log = getLogger('Rkive.MusicFiles')
        log.info("Setting attributes from list for {0}".format(self.media.filename))
        for t,v in l.items():
            log.info("{0}: {1}".format(t.encode('utf-8'),v.encode('utf-8')))
            setattr(self, t, v)

    def print_attrs(self):
        log = getLogger('Rkive.MusicFiles')
        for t,v in self.__dict__.items():
            log.info("Tag: {0} Value: {1}".format(t, v))

    def pprint(self):
        log = getLogger('Rkive.MusicFiles')        
        c = self.media.get_object()
        log.info(c.pprint())

    def __setattr__(self, t, v):
        if t in Media.TagMap:
            if not hasattr(self, 'media'):
                raise MediaObjectNotFound
            setattr(self.media, t, v)
        else:
            self.__dict__[t] =  v

    def save(self):
        log = getLogger('Rkive.MusicFiles')        
        self.media.save()

    def set_attrs(self):
        for t in Media.TagMap:
            v = self.media.get_attr(t)
            if v:
                self.__dict__[t] = v
