# -*- coding: utf-8 -*-
import os.path
from logging import getLogger
from mutagen.id3 import ID3
from mutagen.id3 import error as id3_error
from mutagen.flac import FLAC, Picture
from mutagen.id3 import TIT1, TIT2, TPE3, TPE2, TALB, TPE1, TDAT, TRCK, TCON, TORY, TPUB, TDRC, TPOS, COMM, TCOM, APIC
from PIL import Image
import weakref
from yaml import load

class InvalidTag(Exception): pass

TagMap={
    "grouping" : "Group tracks",
    "album" : "Album name,, unique to artist namespace",
    "albumartist": "The album artist",
    "comment" : "General comments - stuff that can't be put in tags",
    "artist": "Track artist",
    "composer": "This is used by me",
    "discnumber": "Discnumber",
    "disctotal":"Total number of discs",
    "genre":"the genre(s) of the piece",
    "picture":"Picture",
    "title": "Title of track",
    "tracknumber":"Number of track",
    "tracktotal":"Total number of tracks in collection",
    "year":"Year of Release"
}

CueMap = {
    'album_name' : 'album',
    'performer_name' : 'albumartist',
    'track_number' : 'tracknumber',
    'track_name' : 'title'
}

class MP3(object):

    ID3Lookup = {}

    Tags={
        "grouping" : "TIT1",
        "album" : "TALB",
        "albumartist": "TPE2",
        "comment" : "COMM",
        "artist": "TPE1",
        "comment": "COMM",
        "composer": "TCOM",
        "discnumber": "TPOS",
        "disctotal":"TPOS",
        "genre":"TCON",
        "picture":"APIC",
        "title": "TIT2",
        "tracknumber":"TRCK",
        "tracktotal":"TRCK",
        "year":"TDRC"
    }

    def __init__(self, filename):
        log = getLogger('Rkive.MusicFile')
        self.filename = filename
        if self.ID3Lookup:
            return
        for tag,id3tag in self.Tags.items():
            if not tag in TagMap:
                log.fatal("tag {0}, not in global map, talk to the programmer",format(tag))
                continue
            self.ID3Lookup[tag] = {
                "id3tag" : id3tag,
                "id3method" : getattr(mutagen.id3,id3tag)
            }

    def get_object(self):
        try:
            return(ID3(self.filename))
        except id3_error:
            mp3 = ID3()
            mp3.save(self.filename)
            return mp3

    def get_id3_number(self, id3_val, val):
        value = val
        if '/' in id3_val:
            curr_number, curr_total = '/'.split(id3_val)
            value = '/'.join([value, curr_total])
        return value

    def get_id3_total(self, id3_val, val):
        curr_number = val
        if '/' in id3_val:
            curr_number, curr_total = '/'.split(id3_val)
        return '/'.join([curr_number, val])

    def save(self):
        log = getLogger('Rkive.MusicFile')
        log.info("save file {0}".format(self.filename))
        mp3 = self.get_object()
        log.debug("loop through tag values "+str(self.__dict__))

        for rkive_tag, attr in self.__dict__.items():
            if rkive_tag in self.ID3Lookup:
                id3 = self.ID3Lookup[rkive_tag]
                id3tag=id3['id3tag']
                if rkive_tag == 'tracknumber':
                    value = self.get_id3_number(mp3[id3tag], value)
                if rkive_tag == 'tracktotal':
                    value = self.get_id3_total(mp3[id3tag], value)
                if rkive_tag == 'discnumber':
                    value = self.get_id3_number(mp3[id3tag], value)
                if rkive_tag == 'disctotal':
                    value = self.get_id3_total(mp3[id3tag], value)
                log.debug("modifying tag {0} with value {1} ".format(id3tag, value))
                mp3.delall(id3tag)
                mp3.add(id3['id3method'](encoding=3, text=value))
        mp3.save()

class Flac(Music):

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
        log.debug("hello: {0}".format(ext))
        self.media = MediaTypes.Types[ext](filename)
        Tags.id3_reverse_lookup()
        obj = self.media.get_object()
        for tag, value in obj.items():
            log.debug("hello: {0} {1}".format(tag, value))
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
