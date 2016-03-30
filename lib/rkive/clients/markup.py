from rkive.index.musicfile import Media
from logging import getLogger
import xml.etree.ElementTree as ET
"""
<head>
    track_pattern:
</head>
<album>
    <track filename="">
        title:
        artist:
        file:
        tracknumber:
    </track>
</album>
"""
      
def track_decorator(func):
    def func_wrapper(self):
        filename, attrs=func(self)
        return '<track filename="{0}">\n{1}</track>\n'.format(filename, attrs)
    return func_wrapper

class Track(object):
    attribute_types = list(Media.TagMap.keys())
    attribute_types.append('filename')
    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            if name in self.attribute_types:
                setattr(self, name, value) 

    @track_decorator
    def __str__(self):
        buff = ''
        filename = ''
        for name in self.attribute_types:
            if hasattr(self, name):
                value = getattr(self, name)
                if name == 'filename':
                    filename = value
                    continue
                buff = buff + "\t<{0}>{1}</{0}>\n".format(name, value)
        return filename, buff

def album_decorator(func):
    def func_wrapper(self):
        return "<album>\n{0}</album>".format(func(self))
    return func_wrapper

class Album(object):
    
    def __init__(self, tracks):
        self.tracks = tracks
       
    @album_decorator
    def __str__(self):
        buff = ''
        for track in self.tracks:
            buff = buff + str(track)
        return buff

class MarkupWriter(object):    

    def create_track(self, **kwargs):
        return Track(**kwargs)

    def create_album(self, tracks):
        return Album(tracks)

    def write_file(self, fn, albums):
        with open(fn, 'w') as fh:
            fh.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n')
            fh.write('<albums>\n')
            for album in albums:
                fh.write(str(album))
            fh.write('</albums>\n')

class MarkupReader(object):
    def read_file(self, inf):
        log = getLogger('Rkive')
        log.info("input file {0}".format(inf))
        tree = ET.parse(inf)
        print(str(tree))
