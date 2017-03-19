# -*- coding: utf-8 -*-
import os.path
from logging import getLogger
import mutagen
from mutagen.id3 import ID3
from mutagen.id3 import error as id3_error
from mutagen.flac import FLAC, Picture
from PIL import Image
from yaml import load
from rkive.dispatchers import multi, method

class InvalidTag(Exception): pass
class MediaObjectNotFound(Exception): pass
class TypeNotSupported(Exception): pass
class FileNotFound(Exception): pass

#left in for when I remap cuemaps for the new class hierarchy
CueMap = {
    'album_name' : 'album',
    'performer_name' : 'albumartist',
    'track_number' : 'tracknumber',
    'track_name' : 'title'
}

class MusicTags(object):

    def __init__(self):
        self._title = ""
        self._album = ""

    @property 
    def title(self):
        """Title of track"""
        return self._title

    @property
    def album(self): 
        """Album name, unique to artist space"""
        return self._album

    @property 
    def disctotal(self):
        """Total number of discs in pack"""
        return self._disctotal

    @property
    def discnumber(self): 
        """Number of Disc in collection - >=1<=disctotal"""
        return self._discnumber

    @property
    def year(self):
        """Year of release"""
        return self._year

    @property
    def tracktotal(self):
        """Total number of tracks in collection"""
        return self._tracktotal

    @property
    def tracknumber(self):
        """Number of track in collections"""
        return self._tracknumber

    @property
    def grouping(self):
        """Grouping the track belongs to"""
        return self._grouping

    @property
    def comment(self):
        """General comment"""
        return self._comment

    @property
    def composer(self): 
        """Composer of track"""
        return self._composer

    @property
    def artist(self):
        """Track artist: <soloist> (instrument); <soloist> (instrument), conductor:orchestra"""
        return self._artist

    @property
    def albumartist(self):
        """The album artist"""
        return self._artist

    @property
    def genre(self):
        """The genres of a piece, seperated by comma"""

    @property
    def picture(self):
        """Picture - just the front picture"""

    @property
    def part(self):
        """Subtitle for CD"""

    @property
    def lyricist(self):
        """Writer of lyrics"""


class MusicTrack(MusicTags):
    """ A class to be inherited by all Track type classes
    all MusicTrack classes implement two methods - get_track and save
    All MusicTrack classes are iterable"""

    mimetypes={
        '.jpeg': u"image/jpeg",
        '.jpg': u"image/jpeg",
        '.png': u"image/png"
    }

    @classmethod
    def get_rkive_tags(cls):
        """A convenience method for getting the standard tag names."""
        return [n for n in MusicTags.__dict__.keys() if not n.startswith('__')]

    @classmethod
    def get_mime_type(cls, filename):
        """A convenience method for defining mime type"""
        log = getLogger('Rkive.MusicFile')
        fp, ext=os.path.splitext(filename)
        log.info(ext)
        if ext in cls.mimetypes:
            return cls.mimetypes[key]
        raise KeyError

    def get_track(self):
        """ Return the Mutagen object that represents the track"""
        log = getLogger('Rkive.MusicFile')
        log.fatal("Method get_track not implemented")

    def save(self):
        """ Save the tags to the related external file"""
        log = getLogger('Rkive.MusicFile')
        log.fatal("Method save not implemented")

    def print_tags(self):
        log = getLogger('Rkive.MusicFile')
        log.info("Dump tag-value pairs")
        for tag,value in vars(self).items():
            log.info("Tag: {0} Value: {1}".format(tag, value))

    def __iter__(self):
        # first start by grabbing the Class items
        iters = dict((x,y) for x,y in MusicTags.__dict__.items() if x[:2] != '__')

        # then update the class items with the instance items
        iters.update(self.__dict__)

        # now 'yield' through the items
        for x,y in iters.items():
            yield x,y

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        raise KeyError

    def __delitem__(self, key):
        if key in self.__dict__:
            del self.__dict__[key]
            return
        raise KeyError


class MP3(MusicTrack):

    def __init__(self, filename):
        log = getLogger('Rkive.MusicFile')
        self.filename = filename

    class ID3:
    
        @multi
        def id3tag(self, rkive_type):
            return rkive_type.get('id3type')

        @method(tag_type, 'TALB')
        def album(self):
            self.add_id3_tag('TALB', self['album'])

        @method(tag_type, 'part')
        def part(self):
            self.add_id3_tag('TSST', self['part'])

        @method(tag_type, 'lyricist')
        def lyricist(self):
            self.add_id3_tag('TEXT', self['lyricist'])

        @method(tag_type, 'composer')
        def composer(self):
            self.add_id3_tag('TCOM', self['composer'])

        @method(tag_type, 'discnumber')
        def discnumber(self):
            discnumber = self['discnumber'] 
            tposval = self._track['TPOS']
            value = __class__.get_id3_total(discnumber, tposval)
            self.add_id3_tag('TPOS', value)

        @method(tag_type, 'disctotal')
        def disctotal(self):
            total = self['disctotal'] 
            tposvalue = self._track['TPOS']
            value = __class__.get_id3_total(tposvalue, total)
            self.add_id3_tag('TPOS', value)

        @method(tag_type, 'albumartist')
        def albumartist(self):
            self.add_id3_tag('TPE2', self['albumartist'])

        @method(tag_type, 'artist')
        def artist(self):
            self.add_id3_tag('TPE1', self['artist'])

        @method(tag_type, 'title')
        def title(self):
            self.add_id3_tag('TIT1', self['title'])

        @method(tag_type, 'grouping')
        def grouping(self):
            self.add_id3_tag('TIT2', self['grouping'])

        @method(tag_type, 'year')
        def year(self):
            self.add_id3_tag('TYER', self['year'])

        @method(tag_type, 'comment')
        def comment(self):
            self.add_id3_tag('COMM', self['comment'])

        @method(tag_type, 'genre')
        def genre(self):
            self.add_id3_tag('TCON', self['genre'])

        @method(tag_type, 'tracktotal')
        def tracktotal(self):
            total = self['tracktotal'] 
            trckvalue = self._track['TRCK']
            value = __class__.get_id3_total(trckvalue, total)
            self.add_id3_tag('TRCK', value)
       
        @method(tag_type, 'tracknumber')
        def tracknumber(self):
            tracknumber = self['tracknumber'] 
            trckval = self._track['TRCK']
            value = __class__.get_id3_total(tracknumber, trckval)
            self.add_id3_tag('TRCK', value)

        @method(tag_type, 'APIC')
        def picture(self): 
            mimetype=self.get_mime_type(self.filename)
            fh=open(self.filename).read()
            mutangenid3 = getattr(mutagen.id3, tag)
            self._track.add(mutagenid3(encoding=3, mime=mimetype,type=3,desc=u"cover",data=picfh))

    def id3_tag(self, tag, val):
        mutangenid3 = getattr(mutagen.id3, tag)
        self._track.add(mutagenid3(encoding=3, text=value))

    @property 
    def filename(self):
        return self._filename

    @property
    def track(self):
        return self._track

    @track.setter
    def track(self, filename):
        log=getLogger('Rkive.MusicFile')
        self._filename = filename
        try:
            mp3 = ID3(filename)
            log.debug("Return file: {0}".format(self.filename))
            self._track = mp3
        except id3_error:
            log.debug("Adding default ID3 frame to {0}".format(self.filename))
            mp3 = ID3()
            mp3.save(filename)
            self._track = mp3

    @classmethod
    def get_id3_total(cls, id3_val, total):
        log = getLogger('Rkive.MusicFile')
        curr_number = id3_val
        if '/' in id3_val:
            curr_number, curr_total = id3_val.split('/')
        return  '/'.join([curr_number, total])

    def save(self):
        """ Save a MP3 file
        ID3 format has TRCK=Tracknumber/Tracktotal, IPOS=DiscNumber/Disctotal
        the Rkive way is to carry both seperately, so when we come to save
        we need to do come work to reduce two variables to one, if need be
        do that disctotal or discnumber never reach the save loop
        """
        log = getLogger('Rkive.MusicFile')
        log.info("save file {0}".format(self.filename))
        for rkive_tag in self.get_rkive_tags():
            log.debug("cycle through tag: {0}".format(rkive_tag))
            if rkive_tag in dict(self):
                log.debug("modifying tag {0} with value {1} ".format(id3tag, value))
                getattr(__class__.ID3, rkive_tag)(self)
        self._track.save(self.filename)

class Flac(MusicTrack):

    @property
    def track(self):
        return self._track

    @track.setter
    def track(self, filename):
        try:
            self._track = FLAC(filename)
        except mutagen.flac.error:
            flac = FLAC()
            flac.save(filename)
            self._track = flac

    def save(self):
        log = getLogger('Rkive.MusicFile')
        flac = self._track
        if 'picture' in self:
            flac.clear_pictures()
            pic = Picture()
            with open(self.picture, "rb") as f:
                pic.data = f.read()
            im = Image.open(self.picture)
            pic.type = 3
            pic.mime=self.get_mime_type(self.picture)
            pic.width = im.size[0]
            pic.height = im.size[1]
            flac.add_picture(pic)
            del self['picture']
        for rkive_tag in self.get_rkive_tags():
            if hasattr(self, rkive_tag):
                flac[rkive_tag] = self[rkive_tag]
        flac.save()

class FileNotFound(Exception):
    pass

class TypeNotSupported(Exception):
    pass

class TagsObjectNotFound(Exception):
    pass

#
# Proxy Object
class MusicFile(MusicTrack):

    mediatypes = {
        '.mp3'  : MP3,
        '.flac' : Flac
    }

    @classmethod
    def is_music_file(cls, root, name):
        log = getLogger('Rkive.MusicFile')
        log.debug("fp: {0}".format(name))
        for t in cls.mediatypes:
            if (name.endswith(t)):
                return True
        return False

    @property
    def media_class(self, filename):
        basename, mediatype = os.path.splitext(filename)
        if mediatype in self.mediatypes:
            return self.mediatypes[mediatype]
        raise TypeNotSupported

    def set_tags_from_list(self, l):
        log = getLogger('Rkive.MusicFile')
        log.info("Setting attributes from list for {0}".format(self.media.filename))
        for tag,value in l.items():
            log.info("{0}: {1}".format(tag,val))
            setattr(self, tag, val)

    @property
    def track(self):
        return self._media.get_track()

    @property 
    def media(self):
        return self._media

    @media.setter
    def media(self, filename):
        log = getLogger('Rkive.MusicFile')
        basename, ext = os.path.splitext(filename)
        log.info("hello: {0}".format(ext))
        self._media = self.mediatypes[ext][0](filename)
        obj = self._media.get_track()
        for tag in obj:
            if tag in self.get_rkive_tags():
                value = obj[tag]
                self[tag]=value

    def report_tag(self, tag):
        log = getLogger('Rkive.MusicFile')
        log.debug("tag: {0}".format(tag))
        if tag in self.__dict__:
            value = getattr(self, tag)
            log.info("{0}: Attribute {1} has value {2}".format(self.media.filename, tag, value))
        else:
            log.info("{0}: Attribute {1} has not been set".format(self.media.filename, tag))

    def report_unset_tags(self, tags):
        log = getLogger('Rkive.MusicFile')
        if not tags:
            return
        for tag in tags:
            if not tag in self.__dict__:
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
        for tag in self.get_rkive_tags():
            self.report_tag(tag)

    def pprint(self, filename):
        log = getLogger('Rkive.MusicFile')
        self.filename = filename
        c = self.media.get_track()
        log.info(c.pprint())

    def __setattr__(self, tag, value):
        log = getLogger('Rkive.MusicFile')
        if tag in self.get_rkive_tags():
            log.debug("{0}: {1}".format(tag,value))
            self[tag]=value
        elif tag=='filename':
            filename = value
            log.debug("Filename: {0}".format(filename))
            if (not os.path.exists(filename)):
                log.warn("Path not found {0}".format(filename))
                raise FileNotFound
            mediaclass=self.get_media_class(filename)
            log.debug("Tagstype : {0}".format(mediaclass))
            self['media'] = mediaclass(filename)
            log.debug("Tagstype : {0}".format(self['media']))
        else:
            self[tag]=value

    def save(self):
        log = getLogger('Rkive.MusicFiles')
        if not hasattr(self, "media"):
            log.fatal("No media set")
            raise MediaObjectNotFound
        for tag, value in self:
            if tag in self.get_rkive_tags() and value:
                self.media[tag]=value
        self.media.save()
