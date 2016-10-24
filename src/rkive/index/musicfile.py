# -*- coding: utf-8 -*-
import os.path
from logging import getLogger
import mutagen
from mutagen.id3 import ID3
from mutagen.id3 import error as id3_error
from mutagen.flac import FLAC, Picture
from PIL import Image
from yaml import load

class InvalidTag(Exception): pass

#left in for when I remap cuemaps for the new class hierarchy
CueMap = {
    'album_name' : 'album',
    'performer_name' : 'albumartist',
    'track_number' : 'tracknumber',
    'track_name' : 'title'
}

class Tags(object):

    tags={
        'title':'Title of track',
        'album' : 'Album name, unique to artist space',
        'disctotal': 'Total number of discs in pack',
        'discnumber': 'Number of Disc in collection - >=1<=disctotal',
        'year': 'Year of release',
        'tracktotal' : 'Total number of tracks in collection',
        'tracknumber': 'Number of track in collections',
        'grouping':'Grouping the track belongs to',
        'comment': 'General comment',
        'composer':'Composer of track',
        'artist': """Track artist: <soloist> (instrument); <soloist> (instrument), conductor:orchestra""",
        'albumartist':'The album artist',
        'genre':'The generes of piece, seperated by comma',
        'picture':'Picture - just the front picture',
    }

    @classmethod
    def get_tags(cls):
        return self.tags.keys()

class MusicTrack(object):

    def get_object(self):
        log = getLogger('Rkive.MusicFile')
        log.fatal("Method get_object not implemented")

    def save(self):
        log = getLogger('Rkive.MusicFile')
        log.fatal("Method save not implemented")

class MP3(MusicTrack):

    id3tags={
        'genre':'TCON',
        'tracktotal' : 'TRCK',
        'tracknumber':'TRCK',
        'picture' : 'APIC',
        'comment':'COMM',
        'title':'TIT1',
        'grouping':'TIT2',
        'artist':'TPE1',
        'year':'TYER',
        'albumartist':'TPE2',
        'disctotal' : 'TPOS',
        'discnumber':'TPOS',
        'composer':'TCOM',
        'album':'TALB'
    }

    def __init__(self, filename):
        log = getLogger('Rkive.MusicFile')
        self.filename = filename

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
        for rkive_tag in Tags.get_tags():
            if hasattr(self, rkive_tag):
                value = getattr(self, rkive_tag)
                id3tag=self.id3tags[rkive_tag]
                log.debug("Writing tag {0}: {1}".format(id3tag,value))
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
                mp3.add(getattr(mutagen.id3,id3tag)(encoding=3, text=value))
        mp3.save()

class Flac(MusicTrack):

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
        log.debug("Tag: {0}: {1}".format(tag, attr.value))
        for rkive_tag in Tags.get_tags():
            if hasattr(self, rkive_tag):
                flac[rkive_tag] = getattr(self, rkive_tag)
        flac.save()

class FileNotFound(Exception):
    pass

class TypeNotSupported(Exception):
    pass

class TagsObjectNotFound(Exception):
    pass

class MediaTypes(object):

    Types = {
        '.mp3'  : (MP3, ID3Tag),
        '.flac' : (Flac, Tag)
    }

    @classmethod
    def is_music_file(cls, fp):
        log = getLogger('Rkive.MusicFile.MediaTypes')
        log.debug("fp: {0}".format(fp))
        for t in self.Types:
            if (fp.endswith(t)):
                return True
        return False

#
# Proxy Object
class MusicFile(object):

    def set_tags_from_list(self, l):
        log = getLogger('Rkive.MusicFile')
        log.info("Setting attributes from list for {0}".format(self.media.filename))
        for tag,value in l.items():
            log.info("{0}: {1}".format(tag,val))
            setattr(self, tag, val)

    def set_media(self, filename):
        log = getLogger('Rkive.MusicFile')
        basename, ext = os.path.splitext(filename)
        log.debug("hello: {0}".format(ext))
        self.media = MediaTypes.Types[ext][0](filename)
        obj = self.media.get_object()
        for tag in obj:
            if tag in Tags.get_tags():
                rkive_tag = getattr(self.media, tag)
                value = obj[tag]
                setattr(self.media,rkive_tag, value)

    def report_tag(self, tag):
        log = getLogger('Rkive.MusicFile')
        log.debug("tag: {0}".format(tag))
        if hasattr(self,tag):
            value = getattr(self, tag)
            log.info("{0}: Attribute {1} has value {2}".format(self.media.filename, tag, value))
        else:
            log.info("{0}: Attribute {1} has not been set".format(self.media.filename, tag))

    def report_unset_tags(self, tags):
        log = getLogger('Rkive.MusicFile')
        if not tags:
            return
        for tag in tags:
            if not hasattr(self, tag):
                log.info("{0}: Attribute {1} has not been set".format(self.media.filename, tag))

    def report_set_tags(self, tags):
        log = getLogger('Rkive.MusicFile')
        log.debug("report_set_tags")
        if not tags:
            return
        for tag in tags:
            self.report_tag(tag)

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
        if tag in Tags.get_tags():
            log.debug("{0}: {1}".format(tag,value))
            setattr(self, tag, value)
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
            self.__dict__['media'] = MediaTypes.Types[mediatype](filename)
        else:
            self.__dict__[tag]=value

    def save(self):
        log = getLogger('Rkive.MusicFiles')
        if not self.media:
            log.fatal("No media set")
            raise MediaObjectNotFound
        for tag, value in self.__dict__.items():
            if tag in MusicTrack.get_properties() and value:
                setattr(self.media, tag, value)
        self.media.save()
