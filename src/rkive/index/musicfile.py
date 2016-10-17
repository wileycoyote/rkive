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


CueMap = {
    'album_name' : 'album',
    'performer_name' : 'albumartist',
    'track_number' : 'tracknumber',
    'track_name' : 'title'
}
class Tag(object):

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value=v

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, c):
        self._comment=c

class ID3Tag(Tag):

    ID3Tags={
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

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n
        self._func = getattr(mutagen.id3, n)

    @property
    def func(self):
        return self._func

class MusicTrack(object):

    @property
    def title(self):
        """Title of Track"""
        return self._title

    @title.setter
    def title(self, a):
        t = Tag()
        t.name='title'
        t.value = a
        self._album = t
 
    @property
    def album(self):
        """Album name, unique to artist namespace"""
        return self._album

    @album.setter
    def album(self, a):
        t = Tag()
        t.name='album'
        t.value = a
        self._album = t
 
    @property
    def disctotal(self):
        """Total number of discs in pack"""
        return self._disctotal

    @disctotal.setter
    def disctotal(self, n):
        t = Tag()
        t.name='disctotal'
        t.value = n
        self._disctotal = t

    @property
    def year(self):
        """Year of Release"""
        return self._year

    @year.setter
    def year(self, y):
        self._year = y

    @property
    def tracktotal(self):
        """Total number of tracks in collection"""
        return self._tracktotal

    @tracktotal.setter
    def tracktotal(self, t):
        self._tracktotal = t

    @property
    def discnumber(self):
        """Number of disc in collection"""
        return self._discnumber

    @discnumber.setter
    def discnumber(self, d):
        self._discnumber = d

    @property
    def grouping(self):
        """A label to group tracks"""
        return self._grouping

    @grouping.setter
    def grouping(self, g):
        self._grouping=g

    @property
    def comment(self):
        """General comments - stuff that can't be put in tags"""
        return self._comment

    @comment.setter
    def comment(self, c):
        self._comment = c

    @property
    def composer(self):
        """Composer of track"""
        return self._composer

    @composer.setter
    def composer(self, c):
        self._composer = c

    @property
    def artist(self):
        """Track artist"""
        return self._artist

    @artist.setter
    def artist(self, artist):
        self._artist = artist
        self._artist.comment=""

    @property
    def albumartist(self):
        """The album artist"""
        return self._albumartist

    @albumartist.setter
    def albumartist(self, a):
        self._albumartist = a

    @property
    def genre(self):
        "The genre(s) of the piece, each seperated by a comma"""
        return self._genre

    @genre.setter
    def genre(self, g):
        self._genre = g

    @property
    def picture(self):
        """ Picture to display - usually front-cover"""
        return self._picture

    @picture.setter
    def picture(self, p):
        self._picture = p

    def set_rkive_tag(self, tag):
        if tag in TagMap:
            return tag
        return None

class MP3(MusicTrack):

    @grouping.setter
    def grouping(self, g):
        t = ID3Tag()
        t.name='TIT1'

    def __init__(self, filename):
        log = getLogger('Rkive.MusicFile')
        for tag, tag_obj in vars(self):
            setattr(self, tag, ID3Tag()) 
            tag_obj = getattr(self, tag)
            id3tag=ID3Tags[tag]
            tag_obj.id3tag = id3tag
            tag_obj.func = getattr(mutagen.id3,id3tag)
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

    def set_rkive_tag(self, id3tag):
        if id3tag in self.ID3ReverseLookup:
            return self.ID3RevereLookup[id3tag]
        return None

    def save(self):
        log = getLogger('Rkive.MusicFile')
        log.info("save file {0}".format(self.filename))
        mp3 = self.get_object()
        log.debug("loop through tag values "+str(self.__dict__))

        for rkive_tag, attr in vars(self).items():
            if hasattr(self, rkive_tag):
                attr = getattr(self, rkive_tag)
                value = attr.value
                id3tag = attr.name
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
                mp3.add(getattr(attr,'func')(encoding=3, text=value))
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
        for tag, attr in vars(self).items():
            log.debug("Tag: {0}: {1}".format(tag, attr.value))
            if tag in vars(self):
                flac[tag] = attr.value
        flac.save()

class FileNotFound(Exception):
    pass

class TypeNotSupported(Exception):
    pass

class TagsObjectNotFound(Exception):
    pass

class MediaTypes:
    Types = {
        '.mp3'  : (MP3, ID3Tag),
        '.flac' : (Flac, Tag)
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
        for tag,value in l.items():
            log.info("{0}: {1}".format(tag,val))
            setattr(self, tag, val)

    def set_media(self, filename):
        log = getLogger('Rkive.MusicFile')
        basename, ext = os.path.splitext(filename)
        log.debug("hello: {0}".format(ext))
        self.media = MediaTypes.Types[ext][0](filename)
        obj = self.media.get_object()
        tag_class = MediaTypes.Types[ext][1]
        for tag, value in obj.items():
            log.debug("hello: {0} {1}".format(tag, value))
            rkive_tag = self.media.set_rkive_tag(tag)
            if rkive_tag:
                t = tag_class()
                t.value=value
                setattr(self, rkive_tag, t)
            else:
                log.warn("tag {0} not found for {1}".format(tag, filename))

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
        if tag in Tags.TagMap:
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
