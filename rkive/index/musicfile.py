""" Module for accessing music file"""
# -*- coding: utf-8 -*-
import os.path
from logging import getLogger
import mutagen
import mutagen.mp3
from mutagen.flac import FLAC, Picture
from PIL import Image
from mutagen.id3 import ID3NoHeaderError


class InvalidTag(Exception):
    """Invalid tag exception"""


class MediaObjectNotFound(Exception):
    """ To be used when object in memory isn't found"""


class TypeNotSupported(Exception):
    """ What it says on the tin """


class FileNotFound(Exception):
    """ What it says on the tin """


# left in for when I remap cuemaps for the new class hierarchy
CUEMAP = {
    'album_name': 'album',
    'performer_name': 'albumartist',
    'track_number': 'tracknumber',
    'track_name': 'title'
}


class MusicTags:
    """ Interface for mutagen object """

    def __init__(self):
        self._composer = ""
        self._album = ""

    @property
    def title(self):
        """Title of track"""
        return self._title

    @title.setter
    def title(self, t):
        self._title = t

    @property
    def album(self):
        """Album name, unique to artist space"""
        return self._album

    @album.setter
    def album(self, a):
        self._album = a

    @property
    def disctotal(self):
        """Total number of discs in pack"""
        return self._disctotal

    @disctotal.setter
    def disctotal(self, d):
        """Total number of discs in pack"""
        self._disctotal = d

    @property
    def discnumber(self):
        """Number of Disc in collection - >=1<=disctotal"""
        return self._discnumber

    @discnumber.setter
    def discnumber(self, n):
        self._discnumber = n

    @property
    def year(self):
        """Year of release"""
        return self._year

    @year.setter
    def year(self, y):
        self._year = y

    @property
    def tracktotal(self):
        """Total number of tracks in collection"""
        return self._tracktotal

    @tracktotal.setter
    def tracktotal(self, n):
        self._tracktotal = n

    @property
    def tracknumber(self):
        """Number of track in collections"""
        return self._tracknumber

    @tracknumber.setter
    def tracknumber(self, n):
        self._tracknumber = n

    @property
    def grouping(self):
        """Grouping the track belongs to"""
        return self._grouping

    @grouping.setter
    def grouping(self, g):
        self._grouping = g

    @property
    def comment(self):
        """General comment"""
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
        """Track artist: <soloist> (instrument);
        <soloist> (instrument), conductor:orchestra"""
        return self._artist

    @artist.setter
    def artist(self, a):
        self._artist = a

    @property
    def albumartist(self):
        """The album artist"""
        return self._albumartist

    @albumartist.setter
    def albumartist(self, a):
        self._albumartist = a

    @property
    def genre(self):
        """The genres of a piece, seperated by comma"""
        return self._genre

    @genre.setter
    def genre(self, g):
        self._genre = g

    @property
    def picture(self):
        """Picture - just the front picture"""
        return self._picture

    @picture.setter
    def picture(self, p):
        self._picture = p

    @property
    def part(self):
        """Subtitle for CD"""
        return self._part

    @part.setter
    def part(self, p):
        self._part = p

    @property
    def lyricist(self):
        """Writer of lyrics"""
        return self._lyricist

    @lyricist.setter
    def lyricist(self, l):
        self._lyricist = l


class MusicTrack(MusicTags):
    """ A class to be inherited by all Track type classes
    all MusicTrack classes implement two methods - get_track and save
    All MusicTrack classes are iterable"""

    mimetypes = {
        '.jpeg': u"image/jpeg",
        '.jpg': u"image/jpeg",
        '.png': u"image/png"
    }

    @classmethod
    def get_rkive_tags(cls):
        """A convenience method for getting the standard tag names."""
        return [n for n in MusicTags.__dict__.keys() if not n.startswith('__')]

    @classmethod
    def get_tag_comments(cls):
        """ A convenience method for getting the tags and comments"""
        return {
            k: getattr(MusicTags, k).__doc__
            for k in MusicTags.__dict__.keys() if not k.startswith('__')
        }

    @classmethod
    def get_mime_type(cls, filename):
        """A convenience method for defining mime type"""
        log = getLogger('Rkive.MusicFile')
        fp, ext = os.path.splitext(filename)
        log.info(ext)
        if ext in cls.mimetypes:
            return cls.mimetypes[ext]
        raise KeyError

    def save(self):
        """ Save the tags to the related external file"""
        log = getLogger('Rkive.MusicFile')
        log.fatal("Method save not implemented")


class MP3(MusicTrack):

    @classmethod
    def mutagenid3(cls, attr, val):
        mutagenid3 = getattr(mutagen.id3, attr)
        return mutagenid3(encoding=3, text=val)

    @classmethod
    def get_id3_total(cls, id3_val, total=None):
        curr_number = id3_val
        if '/' in id3_val:
            curr_number, curr_total = id3_val.split('/')
        return '/'.join([curr_number, total])

    @property
    def media(self):
        return self._media

    @media.setter
    def media(self, f):
        try:
            mp3 = mutagen.mp3.MP3(f)
        except ID3NoHeaderError:
            mp3 = mutagen.mp3.MP3(f)
            mp3.save()
        except Exception as e:
            print(e)
        self._media = mp3

    @property
    def TALB(self):
        if hasattr(self, 'album'):
            self._TALB = __class__.mutagenid3('TALB', self.album)
        return self._TALB

    @property
    def TSST(self):
        if hasattr(self, 'part'):
            self._TSST = __class__.mutagenid3('TSST', self.part)
        return self._TSST

    @property
    def AUT(self):
        if hasattr(self, 'lyricist'):
            self._AUT = __class__.mutagenid3('AUT', self.lyricist)
        return self._AUT

    @property
    def TCOM(self):
        if hasattr(self, 'COMPOSER'):
            self._TCOM = __class__.mutagenid3('TCOM', self.composer)
        return self._TCOM

    @property
    def TPOS(self):
        value = __class__.get_id3_total(self.discnumber, self.disctotal)
        self._TPOS = __class__.mutagenid3('TPOS', value)
        return self._TPOS

    @property
    def TPE2(self):
        self._TPE2 = __class__.mutagenid3('TPE2', self.albumartist)
        return self._TPE2

    @property
    def TPE1(self):
        self._TPE1 = __class__.mutagenid3('TPE1', self.artist)
        return self._TPE1

    @property
    def TIT1(self):
        self._TIT1 = __class__.mutagenid3('TIT1', self.grouping)
        return self._TIT1

    @property
    def TYER(self):
        self._TYER = __class__.mutagenid3('TYER', self.year)
        return self._TYER

    @property
    def COMM(self):
        self._COMM = __class__.mutagenid3('COMM', self.comment)
        return self._COMM

    @property
    def TCON(self):
        self._TCON = __class__.mutagenid3('TCON', self.genre)
        return self._TCON

    @property
    def TRCK(self):
        value = __class__.get_id3_total(self.tracknumber, self.tracktotal)
        self._TRCK = __class__.mutagenid3('TRCK', value)
        return self._TRCK

    @property
    def APIC(self):
        """ picture """
        mimetype = self.get_mime_type(self.picture)
        picfh = open(self.picture).read()
        mutagenid3 = getattr(__class__.mutagenid3, 'APIC')
        m = mutagenid3(
            encoding=3,
            mime=mimetype,
            type=3,
            desc=u"cover",
            data=picfh
        )
        self._APIC = m
        return self._APIC

    @property
    def TIT2(self):
        self._TIT2 = __class__.mutagenid3('TIT2', self.title)
        return self._TIT2

    def save(self):
        """ Save a MP3 file
        ID3 format has TRCK=Tracknumber/Tracktotal, IPOS=DiscNumber/Disctotal
        the Rkive way is to carry both seperately, so when we come to save
        we need to do come work to reduce two variables to one, if need be
        do that disctotal or discnumber never reach the save loop
        """

        for t in self.__dict__:
            id3t = t[1:]
            if id3t.isupper():
                self._media[id3t] = getattr(self, id3t)
        self._media.save()


class Flac(MusicTrack):

    @property
    def media(self):
        return self._media

    @media.setter
    def media(self, f):
        try:
            flac = FLAC(f)
        except mutagen.flac.error:
            flac = FLAC()
            flac.save(f)
        self._media = flac

    def save(self):
        if 'picture' in self.__dict__:
            self._media.clear_pictures()
            pic = Picture()
            with open(self.picture, "rb") as f:
                pic.data = f.read()
            im = Image.open(self.picture)
            pic.type = 3
            pic.mime = self.get_mime_type(self.picture)
            pic.width = im.size[0]
            pic.height = im.size[1]
            self._media.add_picture(pic)
        for rkive_tag in self.get_rkive_tags():
            a = getattr(self, rkive_tag, False)
            if a:
                self._media[rkive_tag] = a
        self._media.save()


class TagReporter(object):

    def report_tag(self, tag):
        log = getLogger('Rkive.MusicFile')
        log.debug("tag: {0}".format(tag))
        filename = self.media
        if tag in self.__dict__['_media'].__dict__['media']:
            v = getattr(self, tag)
            log.info(f"{filename}: Attribute {tag} has value {v}")
        else:
            log.info(f"{filename}: Attribute {tag} has not been set")

    def unset_tags(self):
        log = getLogger('Rkive.MusicFile')
        for tag in self.rkive_tags:
            if tag not in self.__dict__:
                f = self.media.filename
                log.info(f"{f}: Attribute {tag} has not been set")

    def set_tags(self, tags):
        log = getLogger('Rkive.MusicFile')
        log.debug("report_set_tags")
        for tag in self.get_rkive_tags():
            self.report_tag(tag)

    def all_tags(self):
        log = getLogger('Rkive.MusicFile')
        log.debug("all_tags")
        for tag in MusicTrack.get_rkive_tags():
            self.report_tag(tag)

    def pprint(self, filename):
        log = getLogger('Rkive.MusicFile')
        self.filename = filename
        c = self.media.get_track()
        log.info(c.pprint())


class MusicFile(TagReporter):

    mediatypes = {
        '.mp3': MP3,
        '.flac': Flac
    }

    @classmethod
    def is_music_file(cls, fp):
        log = getLogger('Rkive.MusicFile')
        log.debug("fp: {0}".format(fp))
        for t in cls.mediatypes:
            if (fp.endswith(t)):
                return True
        return False

    @property
    def media(self):
        return self._media

    @media.setter
    def media(self, filename):
        print(filename)
        if not MusicFile.is_music_file(filename):
            return None
        basename, ext = os.path.splitext(filename)
        self._filename = filename
        self._media = self.mediatypes[ext](filename)

    @property
    def tags(self):
        for tag in self._media:
            if tag in self.rkive_tags():
                val = self._media.__dict__[tag]
                self.__dict__[tag] = val
        return {x: y for x, y in self.__dict__.items() if x in self.rkive_tags}

    @tags.setter
    def tags(self, l):
        log = getLogger('Rkive.MusicFile')
        log.info(f"Setting attributes from list for {self.media.filename}")
        for tag, val in l.items():
            if tag in self.rkive_tags():
                log.info(f"{tag}: {val}")
                self.__dict__[tag] = val

    def save(self):
        log = getLogger('Rkive.MusicFiles')
        if not hasattr(self, "_media"):
            log.fatal("No media set")
            raise MediaObjectNotFound
        for tag, value in self.__dict__.items():
            if tag == '_filename':
                continue
            if tag.startswith('_'):
                continue
            if tag in MusicTrack.get_rkive_tags() and value:
                self._media.__dict__[tag] = value
        self._media.save()
