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

class Tags(object):

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

def is_music_file(self, fp):
    for t in Tags.Types:
        if (fp.endswith(t)):
            return True
    return False

class MP3(Tags):

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
        for t, v in self.__dict__.items():
            if t in self.TagMap:
                id3_key, func = self.TagMap[t]['mp3']
                log.debug("modifying tag {0} with value {1} ".format(id3_key, v))
                mp3.delall(id3_key)
                mp3.add(func(encoding=3, text=v))
        mp3.save()

class Flac(Tags):

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
        for t, v in self.__dict__.items():
            log.debug("Tag: {0}: {1}".format(t, v))
            if t in self.TagMap:
                flac[t] = v
        flac.save()

class FileNotFound(Exception):
    pass

class TypeNotSupported(Exception):
    pass

class TagsObjectNotFound(Exception):
    pass
#
# Proxy Object
class MusicFile(object):

    Types = {
        '.mp3'  : MP3,
        '.flac' : Flac
    }

    def __init__(self):
        self.create_report_functions()

    def set_tags_from_list(self, l):
        log = getLogger('Rkive.MusicFiles')
        log.info("Setting attributes from list for {0}".format(self.media.filename))
        for t,v in l.items():
            log.info("{0}: {1}".format(t,v))
            setattr(self, t, v)

    def set_media(self, filename):
        basename, ext = os.path.splitext(filename)
        self.media = Types[ext](filename)
        for t in Tags.TagMap:
            v = self.media.__dict__[t]
            setattr(self, t, v)

    def report_tag(self, t):
        func_name = 'print_{0}'.format(t)
        getattr(self, func_name)()

    def report_select_tags(self, tags):
        log = getLogger('Rkive.MusicFile')
        for t in tags:
            self.report_tag(t)

    def report_all_tags(self):
        for t in Tags.TagMap:
            self.report_tag(t)

    def pprint(self, filename):
        log = getLogger('Rkive.MusicFile')
        self.filename = filename
        c = self.media.get_object()
        log.info(c.pprint())

    def create_report_functions(self):
        log = getLogger('Rkive.MusicFile')
        for t in Tag.TagMap:
            def func(self):
                print("Attribute {0} has not been set".format(t))
            func_name = 'print_{0}'.format(t)
            setattr(self, func_name, func)

    def __setattr__(self, t, v):
        log = getLogger('Rkive.MusicFile')
        if t in Tags.TagMap:
            log.debug("{0}: {1}".format(t,v))
            self.__dict__[ t] = v
            def func(self):
                print("Attribute {0} has been set with value {1}".format(t,v))
            func_name = 'print_{0}'.format(t)
            #
            # monkey patch the attribute print function
            setattr(self, func_name, func)
        elif t=='filename':
            filename = v
            log.info("Filename: {0}".format(filename))
            if (not os.path.exists(filename)):
                log.warn("Path not found {0}".format(filename))
                raise FileNotFound
            basename, mediatype = os.path.splitext(filename)
            log.debug("Tagstype : {0}".format(mediatype))
            if (not mediatype in self.Types):
                raise TypeNotSupported
            if ('.AppleDouble' in filename):
                raise TypeNotSupported
            self.__dict__['media'] = self.Types[mediatype](filename)
        else:
            self.__dict__[t] =  v

    def save(self):
        log = getLogger('Rkive.MusicFiles')
        if not self.media:
            log.fatal("No media set")
            raise MediaObjectNotFound
        for t, v in self.__dict__.items():
            if t in Tags.TagMap and v:
                setattr(self.media, t, v)
        self.media.save()
