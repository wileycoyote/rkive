# -*- coding: utf-8 -*-
import os.path
from logging import getLogger
from mutagen.id3 import ID3
from mutagen.id3 import error as id3_error
from mutagen.flac import FLAC, Picture
from mutagen.id3 import TIT1, TIT2, TPE3, TPE2, TALB, TPE1, TDAT, TRCK, TCON, TORY, TPUB, TDRC, TPOS, COMM, TCOM, APIC
from PIL import Image
import weakref

class InvalidTag(Exception): pass

class Tags(object):

    Id3ReverseLookup = {}

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

    def get_rkive_tagname(t,mt):
        if key in Tags.TagMap:
            return(Tags.TagMap[key][mt])
        return False

    def id3_reverse_lookup():
        for tag,value in Tags.TagMap.items():
            id3 = value['mp3'][0]
            Tags.Id3ReverseLookup[id3] = tag

    def save(self):
        log = getLogger('Rkive.MusicFile')
        log.warn("Save method not instanciated")
        return None

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
        val = None
        id3tag, id3func = self.TagMap['discnumber']['mp3']
        if hasattr(mp3, id3tag):
            valinfile = mp3[id3tag]
            mp3.delall(id3tag)
            if ('/' in valinfile):
                dn, dt = '/'.split(valinfile)
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
            mp3.add(id3func(encoding=1, text=v))
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

class MediaTypes:
    Types = {
        '.mp3'  : MP3,
        '.flac' : Flac
    }


def is_music_file(fp):
    log = getLogger('Rkive.MusicFiles')
    log.debug("fp: {0}".format(fp))
    for t in MediaTypes.Types:
        if (fp.endswith(t)):
            return True
    return False

#
# Proxy Object
class MusicFile(object):

    def set_tags_from_list(self, l):
        log = getLogger('Rkive.MusicFiles')
        log.info("Setting attributes from list for {0}".format(self.media.filename))
        for t,v in l.items():
            log.info("{0}: {1}".format(t,v))
            setattr(self, t, v)

    def set_media(self, filename):
        log = getLogger('Rkive.MusicFile')
        basename, ext = os.path.splitext(filename)
        self.media = MediaTypes.Types[ext](filename)
        Tags.id3_reverse_lookup()
        obj = self.media.get_object()
        for tag, value in obj.items():
            log.debug("attribute to set: {0} {1}".format(tag, value))
            rkive_tag = ''
            if ext == '.mp3':
                if tag in Tags.Id3ReverseLookup:
                    rkive_tag = Tags.Id3ReverseLookup[tag]
            else:
                if tag in Tags.TagMap:
                    rkive_tag = tag
            if rkive_tag:
                setattr(self, rkive_tag, value)

    def make_method_name(self, tag):
        return 'print_{0}'.format(tag)

    def report_tag(self, tag):
        log = getLogger('Rkive.MusicFile')
        log.debug("tag: {0}".format(tag))
        method_name = self.make_method_name(tag)
        log.debug("method_name: {0}".format(method_name))
        if hasattr(self,method_name):
            getattr(self, method_name)(self)
        else:
            log.info("{0}: Attribute {1} has not been set".format(self.media.filename, tag))

    def report_unset_tags(self, tags):
        log = getLogger('Rkive.MusicFile')
        if not tags:
            return
        for tag in tags:
            method_name = self.make_method_name(tag)
            if not hasattr(self, method_name):
                log.info("{0}: Attribute {1} has not been set".format(self.media.filename, tag))

    def report_set_tags(self, tags):
        log = getLogger('Rkive.MusicFile')
        log.debug("report_set_tags")
        if not tags:
            return
        for tag in tags:
            method_name = self.make_method_name(tag)
            if hasattr(self, method_name):
                getattr(self, method_name)(self)

    def report_all_tags(self):
        log = getLogger('Rkive.MusicFile')
        log.debug("report_all_tags")
        for tag in Tags.TagMap:
            self.report_tag(tag)

    def pprint(self, filename):
        log = getLogger('Rkive.MusicFile')
        self.filename = filename
        c = self.media.get_object()
        log.info(c.pprint())

    def __setattr__(self, tag, value):
        log = getLogger('Rkive.MusicFile')
        if tag in Tags.TagMap:
            log.debug("{0}: {1}".format(tag,value))
            self.__dict__[tag] = value
            def func(self):
                print("Attribute {0} has been set with value {1}".format(tag,value))
            func_name = 'print_{0}'.format(tag)
            #
            # monkey patch the attribute print function
            setattr(self, func_name, func)
        elif tag=='filename':
            filename = value
            log.info("Filename: {0}".format(filename))
            if (not os.path.exists(filename)):
                log.warn("Path not found {0}".format(filename))
                raise FileNotFound
            basename, mediatype = os.path.splitext(filename)
            log.debug("Tagstype : {0}".format(mediatype))
            if (not mediatype in MediaTypes.Types):
                raise TypeNotSupported
            if ('.AppleDouble' in filename):
                raise TypeNotSupported
            self.__dict__['media'] = Tags.Types[mediatype](filename)
        else:
            self.__dict__[tag]=value

    def save(self):
        log = getLogger('Rkive.MusicFiles')
        if not self.media:
            log.fatal("No media set")
            raise MediaObjectNotFound
        for tag, value in self.__dict__.items():
            if tag in Tags.TagMap and value:
                setattr(self.media, tag, value)
        self.media.save()
