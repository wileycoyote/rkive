# -*- coding: utf-8 -*-
import os.path
from logging import getLogger
import mutagen.id3
from mutagen.id3 import ID3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC, Picture
from mutagen.id3 import TIT1, TIT2, TPE2, TALB, TPE1, TDAT, TRCK, TCON, TORY, TPUB, TDRC, TPOS, COMM, TCOM, APIC
from PIL import Image

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
            'mp4' : '\xA9grp',
            'mp3' : ['TIT1', TIT1],
            'comment' : 'Grouping'
        },
        'album'    : {
            'mp4' : '\xA9alb',
            'mp3' : ['TALB', TALB],
            'comment' : 'Album Name'
        },
        'albumartist' : {
            'mp3' : ['TPE2', TPE2],
            'mp4' : 'aArt',
            'comment' : 'Album artist set to "Various Artists" for multiple artists'
        },
        'artist'      : {
            'mp3' : ['TPE1', TPE1],
            'mp4' : '\xA9art',
            'comment' : 'Artist, seperate by ; if multiple'
        },
        'comment'     : {
            'mp3' : ['COMM', COMM],
            'mp4' : '\xA9cmt',
            'comment' : 'Comment'
        },
        'composer'    : {
            'mp3' : ['TCOM', TCOM],
            'mp4' : '\xA9wrt',
            'comment' : 'composer'
        },
        'discnumber'  : {
            'mp3' : ['TPOS', TPOS],
            'mp4' : 'disk',
            'comment' : 'disc number',
            'default' : 1
        },
        'disctotal'   : {
            'default' : 1,
            'mp3' : ['TPOS', TPOS],
            'mp4' : 'disk',
            'comment' : 'Number of discs'
        },
        'genre'       : {
            'mp3' : ['TCON',TCON],
            'mp4' :  '\xA9gen',
            'comment' : 'Only one genre'
        },
        'picture'     : {
            'mp3' : ['APIC', APIC]
        },
        'title'       : {
            'mp3' : ['TIT2', TIT2],
            'mp4' :  '\xA9nam',
            'comment' : 'title'
        },
        'tracknumber' : {
            'mp3' : ['TRCK', TRCK],
            'mp4' : 'trkn',
            'comment' : 'tracknumber - start from 1'
        },
        'tracktotal'  : {
            'default' : 1,
            'comment' : 'total number of tracks'
        },
        'year'        : {
            'mp3' : ['TDRC', TDRC],
            'mp4' :  '\xA9day',
            'comment' : 'Year of original recording, remaster dates go in comment'
        }
    } 

    def set_media(self):
        pass
    
    def read(self):
        self.set_media()

    def set_media(self):
        pass

    def pprint(self):
        log = getLogger('Rkive.Music')
        tags = self.media.pprint()
        log.info(tags)

    def save(self):
        self.media.save()

    def set_tag(self, t, v):
        setattr(self, t, v)

    def get_tag_names(self):
        return self.media.keys()
    
    def get_tags(self):
        tags = {}
        for t,v in self.media.iteritems():
            tags[t] = v
        return tags

class mp4(Media):

    def set_media(self, filename):
        try:
       	    self.media = MP4(filename)
        except mutagen.mp4.error:
            self.media = MP4()
            self.media.save(filename)
        self.filename = filename

class MP3(Media):
    
    def set_media(self, filename):
        try:
            self.media = ID3(filename)
        except mutagen.id3.error:
            self.media = ID3()
            self.media.save(filename)
        self.filename = filename

    def save(self):
        log = getLogger('Rkive.MusicFile')
        log.info("save file")
        discnumber = None
        disctotal = None
        if (hasattr(self, 'discnumber')):
            discnumber = getattr(self, 'discnumber') 
        if (hasattr(self, 'disctotal')):
            disctotal = getattr(self, 'disctotal')
        v = None
        k, f = self.TagMap['discnumber']['mp3']
        if (k in self.media):
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
            if (not hasattr(self, t)):
                continue
            v = getattr(self, t)
            log.info("real_t "+t)
            if (v):
                k, f = self.TagMap[t]['mp3']
                log.info("modifying real_t "+k)
                self.media.delall(k)
                v = v.decode('utf-8')
                self.media.add(f(encoding=3, text=unicode(v)))
        self.media.save()
        

class Flac(Media):
   
    def set_media(self, filename):
        try:
            self.media = FLAC(filename)
        except mutagen.flac.error:
            self.media = FLAC()
            self.media.save(filename)
        self.filename = filename

    def save(self):
        log = getLogger('Rkive')
        log.info("save file")
        if hasattr(self,'picture'):
            self.media.clear_pictures()
            pic = Picture()
            v = getattr(self, 'picture')
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
            self.save()
            delattr(self, 'picture')
        for t in self.TagMap:
            if hasattr(self, t):
                v = getattr(self, t)
                if v:
                    log.info("{0}: {1}".format(t.encode('utf-8'), v.encode('utf-8')))
                    self.media[t] = v
        self.media.save()

class FileNotFound(Exception):
    pass

class TypeNotSupported(Exception):
    pass

class MusicFile(object):

    Types = {
        'mp4'  : mp4,
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
        log.info("Ext: {0}".format(ext))
        if (not ext in self.Types):
            raise TypeNotSupported 
        if ('.AppleDouble' in filename):
            raise TypeNotSupported
        self.media = self.Types[ext]()
        self.media.set_media(filename)

    def set_tags(self, parent):
        log = getLogger('Rkive.MusicFiles')
        for m in Media.TagMap:
	    try:
            	v = getattr(parent, m)
            	if (v != None):
                    log.info("attribute to modify: {0} {1}".format(m,v))
                    setattr(self.media, m, v)
 	    except AttributeError as e:
                log.info("Attribute error {0} ".format(e))
    
    def set_tags_from_list(self, l):
        log = getLogger('Rkive.MusicFiles')
        log.info("Setting attributes from list for {0}".format(self.media.filename))
        for t,v in l.iteritems():
            if (t in Media.TagMap):
                log.info("{0}: {1}".format(t.encode('utf-8'),v.encode('utf-8')))
                setattr(self.media, t, v)

    def get_tag_names(self):
        return self.media.get_tag_names()

    def get_number_of_tags(self):
        return len(self.media.get_tags())

    def get_tags(self):
        return self.media.get_tags()

    def pprint(self):
        self.media.pprint()
             
    def save(self):
        self.media.save() 
