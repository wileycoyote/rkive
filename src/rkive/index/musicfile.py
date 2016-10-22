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
class Tag(object):
    """Primary container for handling Meta data for Music Files """
    def __init__(self, name='', value=''):
        self.name=name
        self.value=value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name=n

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value=v

class ID3Tag(Tag):
    """Container for ID3 name of tag, plus the function related to that tag """

    @property
    def id3name(self):
        return self._id3name

    @id3name.setter
    def id3name(self, n):
        self._id3name = n
        self.func = getattr(mutagen.id3, n)

    @property
    def func(self):
        return self._func

    @func.setter
    def func(self, f):
        self._func = f

class MusicTrack(object):

    @classmethod
    def get_properties(cls):
        return [p for p in cls.__dict__.keys() if
                not p.startswith('__') and not p.startswith('get') and not p.startswith('save')]

    @property
    def title(self):
        """Title of Track"""
        return self._title

    @title.setter
    def title(self, a):
        self._title=Tag('title', a)

    @property
    def album(self):
        """Album name, unique to artist namespace"""
        return self._album

    @album.setter
    def album(self, a):
        self._album = Tag('album', a)

    @property
    def disctotal(self):
        """Total number of discs in pack"""
        return self._disctotal

    @disctotal.setter
    def disctotal(self, n):
        self._disctotal=Tag('disctotal', n)

    @property
    def year(self):
        """Year of Release"""
        return self._year

    @year.setter
    def year(self, y):
        self._year=Tag('year',y)

    @property
    def tracktotal(self):
        """Total number of tracks in collection"""
        return self._tracktotal

    @tracktotal.setter
    def tracktotal(self, t):
        self._tracktotal = Tag('tracktotal',t)

    @property
    def tracknumber(self):
        """Sequential number of track in collection"""
        return self._tracknumber

    @tracktotal.setter
    def tracktotal(self, t):
        self._tracknumber = Tag('tracknumber',t)

    @property
    def discnumber(self):
        """Number of disc in collection"""
        return self._discnumber

    @discnumber.setter
    def discnumber(self, d):
        self._discnumber = Tag('discnumber',d)

    @property
    def grouping(self):
        """A label to group tracks"""
        return self._grouping

    @grouping.setter
    def grouping(self, g):
        self._grouping=Tag('grouping',g)

    @property
    def comment(self):
        """General comments - stuff that can't be put in tags"""
        return self._comment

    @comment.setter
    def comment(self, c):
        self._comment = Tag('comment',c)

    @property
    def composer(self):
        """Composer of track"""
        return self._composer

    @composer.setter
    def composer(self, c):
        self._composer = Tag('composer',c)

    @property
    def artist(self):
        """Track artist"""
        return self._artist

    @artist.setter
    def artist(self, a):
        self._artist = Tag('artist',a)

    @property
    def albumartist(self):
        """The album artist"""
        return self._albumartist

    @albumartist.setter
    def albumartist(self, a):
        self._albumartist = Tag('albumartist',a)

    @property
    def genre(self):
        """The genre(s) of the piece, each seperated by a comma"""
        return self._genre

    @genre.setter
    def genre(self, g):
        self._genre = Tag('genre',g)

    @property
    def picture(self):
        """ Picture to display - usually front-cover"""
        return self._picture

    @picture.setter
    def picture(self, p):
        self._picture = Tag('picture',p)

class MP3(MusicTrack):

    @property
    def TDRC(self):
        return "year"

    @MusicTrack.year.setter
    def year(self, t):
        self._title=ID3Tag('TDRC', t)

    @property
    def TIT2(self):
        return 'title'

    @MusicTrack.title.setter
    def title(self, t):
        self._title=ID3Tag('TIT2', t)

    @property
    def TRCK(self):
        return "tracknumber"

    @MusicTrack.tracktotal.setter
    def tracktotal(self, t):
        """MP3 does not have a concept of seperate tracknumber and track total
        However, Rkive does - so the ID3tag for tracktotal is the same as tracknumber
        The "tracknumber/tracktotal" string is calculated on write to MP3 file
        """
        self._tracktotal=ID3Tag('TRCK', t)

    @MusicTrack.tracknumber.setter
    def tracknumber(self, t):
        self._tracknumber=ID3Tag('TRCK', t)

    @MusicTrack.picture.setter
    def picture(self, p):
        self._picture=ID3Tag('APIC', p)

    @MusicTrack.disctotal.setter
    def disctotal(self, v):
        self._disctotal=ID3Tag('TPOS', v)

    @MusicTrack.genre.setter
    def genre(self, g):
        self._genre=ID3Tag('TCON', g)

    @MusicTrack.discnumber.setter
    def discnumber(self, d):
        self._discnumber=ID3Tag('TPOS',d)

    @MusicTrack.composer.setter
    def composer(self, c):
        self._composer=ID3Tag('TCOM',c)

    @MusicTrack.artist.setter
    def artist(self, a):
        self._artist=ID3Tag('TPE1', a)

    @MusicTrack.albumartist.setter
    def albumartist(self, a):
        self._albumartist = ID3Tag('TPE2', a)

    @MusicTrack.comment.setter
    def comment(self, c):
        self._comment=ID3Tag('COMM', c)

    @MusicTrack.album.setter
    def album(self, g):
        self._album = ID3Tag('TALB', c)

    @MusicTrack.grouping.setter
    def grouping(self, g):
        self._grouping = ID3Tag('TIT1', g)

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
        for rkive_tag in MusicTrack.get_properties():
            if hasattr(self, rkive_tag):
                attr = getattr(self, rkive_tag)
                value = attr.value
                id3tag = attr.name
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
            if tag in self.media.get_properties():
                rkive_tag = getattr(self.media, tag)
                value = obj[tag]
                setattr(self, rkive_tag, value)

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
        if tag in MusicTrack.get_properties():
            log.debug("{0}: {1}".format(tag,value))
            #
            # MP3 combines the tracknumber/tracktotal and discnumber/disctotal
            if '/' in value:
                if tag=='tracknumber':
                    value, tracktotal = value.split('/')
                    setattr(self, 'tracktotal', tracktotal)
                if tag=='discnumber':
                    value,disctotal = value.split('/')
                    setattr(self, 'disctotal', disctotal)
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
            if tag in Tags.TagMap and value:
                setattr(self.media, tag, value)
        self.media.save()
