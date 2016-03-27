from rkive.index.musicfile import Media
from logging import getLogger
"""
<head>
    track_pattern:
</head>
<album>
    folder:
    title:
    artist:
    composer:
    <track>
        title:
        artist:
        file:
        tracknumber:
    </track>
</album>
"""
class Attributes(object):

    def set_attributes(self, **kwargs):
        for name, value in kwargs.items():
            if name in self.attribute_types:
                setattr(self, name, value) 

    def get_attributes(self):
        buff = ''
        for name in self.attribute_types:
            if hasattr(self, name):
                value = getattr(self, name)
                buff = buff + "\t<{0}>{1}</{0}>\n".format(name, value)
        return buff

def track_decorator(func):
    def func_wrapper(self):
        return "<track>\n{0}</track>\n".format(func(self))
    return func_wrapper

class Track(Attributes):
    attribute_types = Media.TagMap.keys()

    def __init__(self, **kwargs):
        self.set_attributes(**kwargs)

    @track_decorator
    def __str__(self):
        return self.get_attributes()

def album_decorator(func):
    def func_wrapper(self):
        return "<album>\n{0}</album>".format(func(self))
    return func_wrapper

class Album(Attributes):
    
    attribute_types = [
        'folder' 
    ]

    def __init__(self, tracks, **kwargs):
        self.tracks = tracks
        self.set_attributes(**kwargs)
       
    @album_decorator
    def __str__(self):
        buff = self.get_attributes()
        for track in self.tracks:
            buff = buff + str(track)
        return buff

def head_decorator(func):
    def func_wrapper(self):
        return "<header>\n{0}</header>\n".format(func(self))
    return func_wrapper

class Header(Attributes):
    
    attribute_types = ['track_pattern']

    def __init__(self, **kwargs):
        self.set_attributes(**kwargs)

    @head_decorator
    def __str__(self):
        return self.get_attributes()

class MarkupWriter(object):    

    def create_header(self, **kwargs):
        return Header(**kwargs)

    def create_track(self, **kwargs):
        return Track(**kwargs)

    def create_album(self, tracks, **kwargs):
        return Album(tracks, **kwargs)

    def write_file(self, fn, header, albums):
        with open(fn, 'w') as fh:
            fh.write(str(header))
            for album in albums:
                fh.write(str(album))

class MarkupReader(object):
    def read_file(self, inf, funcs=[]):
        log = getLogger('Rkive')
        log.info("input file {0}".format(inf))
        with open(inf,'r') as i:
            line_counter = 0
            record = []
            header = i.readline().strip().split(',')
            size_record = int(header[1])
            for l in i:
                line_counter = line_counter + 1
                record.append(l.strip())
                if line_counter%size_record == 0:
                    for func in funcs:
                        func(header, record)
                    record = []
