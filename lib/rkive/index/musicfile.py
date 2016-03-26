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

    def get_class(self):
        log = getLogger('Rkive.MusicFile')
        log.warn("Class object not instanciated")
        return None

    def save(self):
        log = getLogger('Rkive.MusicFile')
        log.warn("Save method not instanciated")
        return None

    def set_obj(self):
        log = getLogger('Rkive.MusicFile')
        log.warn("Save method not instanciated")

    def get_obj(self):
        log = getLogger('Rkive.MusicFile')
        if self.obj is None:
            log.warn("No object set")
            return None
        return self.obj

class MP3(Media):
  
    def __init__(self, filename):
        self.filename = filename
        self.set_object()

    def set_object(self):
        try:
            mp3 = ID3(self.filename)
            self.obj = mp3
        except id3_error:
            mp3 = ID3()
            mp3.save(self.filename)
            self.obj = mp3

    def get_attr(self, name):
        if not name in self.TagMap:
            return ""
        realname = self.TagMap[name]['mp3'][0]
        if realname in self.obj:
            return self.obj[realname].text[0]
        else:
            return ""

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

    def __init__(self, filename):
        self.filename = filename
        self.set_object()

    def set_object(self):
        try:
            self.obj = FLAC(self.filename)
        except mutagen.flac.error:
            flac = FLAC()
            flac.save(self.filename)
            self.obj = flac 

    def get_attr(self, name):
        if not name in self.TagMap:
            return ""
        realname = self.TagMap[name]['flac'][0]
        if realname in self.obj:
            return self.obj[name]
        else:
            return ""

    def set_attr(self, name, value):
        log = getLogger('Rkive.MusicFile')                
        if not name in self.TagMap:
            return
        if name == 'picture':
            flac = self.obj
            flac.clear_pictures()
            pic = Picture()
            with open(self.picture, "rb") as f:
                pic.data = f.read()
            im = Image.open(self.picture)
            pic.type = 3
            v = getattr('picture')
            if v.endswith('jpg'):
                pic.mime = u"image/jpeg"
            if v.endswith('png'):
                pic.mime = u"image/png"
            pic.width = im.size[0] 
            pic.height = im.size[1]
            flac.add_picture(pic)
            return
        log.debug("Tag: {0}: {1}".format(name, value))
        value = value.encode('utf-8')
        self.obj[name] = value.decode('utf-8')

    def save(self):
        log = getLogger('Rkive.MusicFile')
        log.info("save file {0}".format(self.filename))
        self.obj.save()


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

    def set_filename(self, filename):
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
            if (t in Media.TagMap):
                log.info("{0}: {1}".format(t.encode('utf-8'),v.encode('utf-8')))
                setattr(self, t, v)

    def print_attrs(self):
        log = getLogger('Rkive.MusicFiles')
        for m in Media.TagMap:
            if not hasattr(self, m): 
                continue
            v = getattr(self, m)
            if v:
                log.info("Tag: {0} Value: {1}".format(m, v))

    def pprint(self):
        log = getLogger('Rkive.MusicFiles')        
        c = self.media.get_obj()
        log.info(c.pprint())

    def set_attr(self, t, v):
        self.media.set_attr(t, v)

    def save(self):
        log = getLogger('Rkive.MusicFiles')        
        self.media.save()

    def set_attrs(self):
        for t,v in Media.TagMap.items():
            value = self.media.get_attr(t)
            if value:
                setattr(self, t, value)
