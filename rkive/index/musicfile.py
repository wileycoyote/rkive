# -*- coding: utf-8 -*-
import os.path
from logging import getLogger
import mutagen
from mutagen.id3 import ID3
from mutagen.id3 import error as id3_error
from mutagen import MutagenError
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
        self._disctotal = 0
        self._discnumber = 0
        self._year = 1800
        self._track = None
        self._tracknumber = 0
        self._tracktotal = 0
        self._grouping = ""
        self._comment = ""
        self._composer = ""
        self._artist = ""
        self._albumartist = ""
        self._genre = ""
        self._picture = ""
        self._part = ""
        self._lyricist = ""

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
        return self._genre

    @property
    def picture(self):
        """Picture - just the front picture"""
        return self._picture

    @property
    def part(self):
        """Subtitle for CD"""
        return self._part

    @property
    def lyricist(self):
        """Writer of lyrics"""
        return self._lyricist


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

    def save(self):
        """ Save the tags to the related external file"""
        log = getLogger('Rkive.MusicFile')
        log.fatal("Method save not implemented")

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

    def __init__(self):
        log = getLogger('Rkive.MusicFile')
        self._filename = None
        self._track = None

    class ID3:
    
        @classmethod
        def mutagenid3(cls, attr, val):
            mutangenid3 = getattr(mutagen.id3, attr)
            return mutagenid3(encoding=3, text=val)

        @classmethod
        def get_id3_total(cls, id3_val, total):
            log = getLogger('Rkive.MusicFile')
            curr_number = id3_val
            if '/' in id3_val:
                curr_number, curr_total = id3_val.split('/')
            return  '/'.join([curr_number, total])

        @multi
        def id3tag(cls, rkive_type):
            return rkive_type.get('type')

        @method(id3tag, 'album')
        def tag(album):
            return __class__.mutagenid3('TALB', album['value'])

        @method(id3tag, 'part')
        def tag(part):
            return __class__.mutagenid3('TSST', part['value'])

        @method(id3tag, 'lyricist')
        def tag(lyricist):
            return __class__.mutagenid3('TEXT', lyricist['value'])

        @method(id3tag, 'composer')
        def tag(composer):
            return __class__.mutagenid3('TCOM', composer['value'])

        @method(id3tag, 'discnumber')
        def tag(disnumber):
            given_discnumber = discnumber['value'] 
            tposval = discnumber['parent']._track['TPOS']
            value = __class__.get_id3_total(given_discnumber, tposval)
            return __class__.mutagenid3('TPOS', value)

        @method(id3tag, 'disctotal')
        def tag(parent):
            total = parent['disctotal'] 
            tposvalue = parent._track['TPOS']
            value = __class__.get_id3_total(tposvalue, total)
            return __class__.mutagenid3('TPOS', value)

        @method(id3tag, 'albumartist')
        def tag(aa):
            parent.add_id3_tag('TPE2', self['albumartist'])
            return __class__.mutagenid3('TPOS', value)

        @method(id3tag, 'artist')
        def tag(parent):
            parent.add_id3_tag('TPE1', self['artist'])
            return __class__.mutagenid3('TPOS', value)

        @method(id3tag, 'title')
        def tag(parent):
            parent.add_id3_tag('TIT1', self['title'])
            return __class__.mutagenid3('TPOS', value)

        @method(id3tag, 'grouping')
        def tag(parent):
            parent.add_id3_tag('TIT2', self['grouping'])
            return __class__.mutagenid3('TPOS', value)

        @method(id3tag, 'year')
        def tag(parent):
            return __class__.mutagenid3('TYER', value)

        @method(id3tag, 'comment')
        def tag(parent):
            return __class__.mutagenid3('COMM', parent['value'])

        @method(id3tag, 'genre')
        def tag(parent):
            return __class__.mutagenid3('TCON', parent['value'])

        @method(id3tag, 'tracktotal')
        def tag(tracktotal):
            total = tracktotal['value'] 
            parent = tracktoal['']
            trckvalue = parent._track['TRCK']
            value = __class__.get_id3_total(trckvalue, total)
            return __class__.mutagenid3('TRCK', value)
       
        @method(id3tag, 'tracknumber')
        def tag(tracknumber):
            value = tracknumber['value'] 
            parent = tracknumber['parent'] 
            trckval = parent._track['TRCK']
            value = __class__.get_id3_total(tracknumber, trckval)
            return __class__.mutagenid3('TRCK', value)

        @method(id3tag, 'picture')
        def tag(picture): 
            file = picture['value']
            mimetype=self.get_mime_type(file)
            picfh=open(file).read()
            mutangenid3 = getattr(mutagen.id3, 'APIC')
            return(mutagenid3(encoding=3, mime=mimetype,type=3,desc=u"cover",data=picfh))

    @property
    def tag(self, t):
        return self._track[t]

    @tag.setter
    def tag(self, t, v):
        self._track[t] = v

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
        print('XXXXXXXXXXXXXXXxxx'+filename)
        try:
            mp3 = ID3(filename)
            log.debug("Return file: {0}".format(self.filename))
            self._track = mp3
        except id3_error:
            print("YYYYYYYYYYYYYYYYYYYYY")
            log.debug("Adding default ID3 frame to {0}".format(self.filename))
            mp3 = ID3()
            mp3.save(filename)
            self._track = mp3
        except MutagenError:
            log.fatal("File {0} does not exist")

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
                id3 = __class__.ID3.tag({'type': rkive_tag, 'value': self[rkive_tag], 'parent': self})
                self._track.add(id3)

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

    @property
    def tag(self, t):
        return self._track[t]

    @tag.setter
    def tag(self, t, v):
        self._track[t] = v

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

class TagReporter(object):
    def report_tag(self, tag):
        log = getLogger('Rkive.MusicFile')
        log.debug("tag: {0}".format(tag))
        if tag in self.__dict__:
            value = getattr(self, tag)
            log.info("{0}: Attribute {1} has value {2}".format(self.media.filename, tag, value))
        else:
            log.info("{0}: Attribute {1} has not been set".format(self.media.filename, tag))

    def unset_tags(self):
        log = getLogger('Rkive.MusicFile')
        for tag in self.rkive_tags:
            if not tag in self.__dict__:
               log.info("{0}: Attribute {1} has not been set".format(self.media.filename, tag))

    def set_tags(self, tags):
        log = getLogger('Rkive.MusicFile')
        log.debug("report_set_tags")
        for tag in self.rkive_tags:
            self.report_tag(tag)

    def all_tags(self):
        log = getLogger('Rkive.MusicFile')
        log.debug("report_all_tags")
        for tag in self.rkive_tags:
            self.report_tag(tag)

    def pprint(self, filename):
        log = getLogger('Rkive.MusicFile')
        self.filename = filename
        c = self.media.get_track()
        log.info(c.pprint())

#
# Proxy Object
class MusicFile(MusicTrack, TagReporter):

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
    def media(self):
        return self._media

    @media.setter
    def media(self, filename):
        log = getLogger('Rkive.MusicFile')
        if not MusicFile.is_music_file(filename):
            return None
        basename, ext = os.path.splitext(filename)
        self._media = self.mediatypes[ext][0]()
        self._media.track = filename

    @property 
    def tags(self):
        for tag in self._media:
            if tag in self.rkive_tags():
                value = self._media[tag]
                self[tag]=value
        return {x: y for x,y in self.__dict__.items() if x in self.rkive_tags}

    @tags.setter
    def tags(self, l):
        log = getLogger('Rkive.MusicFile')
        log.info("Setting attributes from list for {0}".format(self.media.filename))
        for tag,value in l.items():
            log.info("{0}: {1}".format(tag,val))
            setattr(self, tag, val)
  
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
            self.media = filename
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
                self.media.track.tag = (tag, value)
        self.media.save()
