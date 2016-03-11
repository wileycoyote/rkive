# -*- coding: utf-8 -*-
import os.path
from logging import getLogger
import mutagen.id3
from mutagen.id3 import ID3
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
            'mp3' : ['TIT1', TIT1],
            'comment' : 'Grouping'
        },
        'album'    : {
            'mp3' : ['TALB', TALB],
            'comment' : 'Album Name'
        },
        'albumartist' : {
            'mp3' : ['TPE2', TPE2],
            'comment' : 'Album artist set to "Various Artists" for multiple artists'
        },
        'artist'      : {
            'mp3' : ['TPE1', TPE1],
            'comment' : 'Artist, seperate by ; if multiple'
        },
        'comment'     : {
            'mp3' : ['COMM', COMM],
            'comment' : 'Comment'
        },
        'composer'    : {
            'mp3' : ['TCOM', TCOM],
            'comment' : 'composer'
        },
        'discnumber'  : {
            'mp3' : ['TPOS', TPOS],
            'comment' : 'disc number',
            'default' : 1
        },
        'disctotal'   : {
            'default' : 1,
            'mp3' : ['TPOS', TPOS],
            'comment' : 'Number of discs'
        },
        'genre'       : {
            'mp3' : ['TCON',TCON],
            'comment' : 'Only one genre'
        },
        'picture'     : {
            'mp3' : ['APIC', APIC],
            'comment' : 'The filename for a image associated with file'
        },
        'title'       : {
            'mp3' : ['TIT2', TIT2],
            'comment' : 'title'
        },
        'tracknumber' : {
            'mp3' : ['TRCK', TRCK],
            'comment' : 'tracknumber - start from 1'
        },
        'tracktotal'  : {
            'default' : 1,
            'comment' : 'total number of tracks'
        },
        'year'        : {
            'mp3' : ['TDRC', TDRC],
            'comment' : 'Year of original recording, remaster dates go in comment'
        }
    } 

    def __init__(self,parent):
        self.parent = weakref.ref(parent) 
        for t in self.TagMap:
            g = lambda: getattr(self.media,t)
            s = lambda x,y: setattr(self.media, t, y)
            d = lambda: delattr(self.media, t) 
            property(g, s, d, t)

    def set_media(self):
        pass
    
    def read(self):
        self.set_media()

    def set_media(self):
        pass

    def print_media(self):
        log = getLogger('Rkive.Music')
        tags = self.media.pprint()
        log.info("Tags for {0}".format(self.filename))
        log.info(tags)

    def save(self):
        self.media.save()

    def get_media_tag_names(self):
        return self.media.keys()
    
    def get_tags(self):
        tags = {}
        for t,v in self.items():
            tags[t] = v
        return tags

class MP3(Media):
   
    def __init__(self, parent):
        Media.__init__(parent)

    def set_media(self, filename):
        try:
            self.media = ID3(filename)
        except mutagen.id3.error:
            self.media = ID3()
            self.media.save(filename)
        self.filename = filename

    def save(self):
        log = getLogger('Rkive.MusicFile')
        log.info("save file {0}".format(self.filename))
        discnumber = None
        disctotal = None
        parent = self.parent
        if (hasattr(parent, 'discnumber')):
            discnumber = getattr(parent, 'discnumber') 
        if (hasattr(parent, 'disctotal')):
            disctotal = getattr(parent, 'disctotal')
        v = None
        k, f = self.TagMap['discnumber']['mp3']
        if hasattr(self.media, k):
            c = self.media[k]
            self.media.delall(k)
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
            self.media.add(f(encoding=1, text=unicode(v)))
        for t in self.TagMap:
            if t == 'discnumber':
                continue
            if t == 'disctotal':
                continue
            if (not hasattr(parent, t)):
                continue
            v = getattr(parent, t)
            log.debug("loop through tag values")
            if (v):
                k, f = self.TagMap[t]['mp3']
                log.debug("modifying tag {0} with value {1} ".format(k, v))
                self.media.delall(k)
                self.media.add(f(encoding=3, text=unicode(v.decode('utf-8'))))
        self.media.save()

class Flac(Media):
   
    def __init__(self, parent):
        Media.__init__(self, parent)

    def set_media(self, filename):
        try:
            self.media = FLAC(filename)
        except mutagen.flac.error:
            self.media = FLAC()
            self.media.save(filename)
        self.filename = filename

    def save(self):
        log = getLogger('Rkive')
        parent = self.parent
        if hasattr(parent,'picture'):
            self.media.clear_pictures()
            pic = Picture()
            v = getattr(parent, 'picture')
            with open(v, "rb") as f:
                pic.data = f.read()
            im = Image.open(v)
            pic.type = 3
            if v.endswith('jpg'):
                pic.mime = u"image/jpeg"
            if v.endswith('png'):
                pic.mime = u"image/png"
            pic.width = im.size[0] 
            pic.height = im.size[1]
            self.media.add_picture(pic)
            delattr(parent, 'picture')
        for t in self.TagMap:
            if hasattr(parent, t):
                v = getattr(parent, t)
                log.debug("{0}: {1}".format(t,v))
                if v:
                    log.debug("{0}: {1}".format(t, v))
                    v = v.encode('utf-8')
                    self.media[t] = v.decode('utf-8')
        self.media.save()

class FileNotFound(Exception):
    pass

class TypeNotSupported(Exception):
    pass

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
        ext = filename.rsplit('.', 1)[1]
        if (not ext in self.Types):
            raise TypeNotSupported 
        if ('.AppleDouble' in filename):
            raise TypeNotSupported
        self.media = self.Types[ext](self)
        self.filetype = ext
        self.media.set_media(filename)
        self.set_tags()

    def set_tag(self, t, v):
        log = getLogger('Rkive.MusicFile')
        if t in Media.TagMap:
            setattr(self,t,v)
        else:
            log.warn("No such tag {0} in Media.TagMap".format(t))

    def set_tags(self):
        for t in Media.TagMap:
            actual_tag = Media.TagMap[self.filetype] 
            if hasattr(self.media, actual_tag):
                v = getattr(self.media, actual_tag)
                setattr(self, t, v)
    
    def set_tags_from_list(self, l):
        log = getLogger('Rkive.MusicFiles')
        log.info("Setting attributes from list for {0}".format(self.media.filename))
        for t,v in l.items():
            if (t in Media.TagMap):
                log.info("{0}: {1}".format(t.encode('utf-8'),v.encode('utf-8')))
                setattr(self, t, v)

    def pprint(self):
        log = getLogger('Rkive.MusicFiles')
        for m in Media.TagMap:
            v = getattr(self, m)
            if v:
                log.info("Tag: {0} Value: {1}".format(m, v))

    def dump_media(self):
        self.media.pprint()

    def save(self):
        self.media.save() 
