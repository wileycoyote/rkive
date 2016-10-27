import unittest
from rkive.index.musicfile import MusicTrack, Tags
import sys
import logging
import string
import random
from testfixtures import LogCapture as LogCapture
from rkive.clients.log import LogInit

def str_generator(size=random.randrange(0, 101, 2), chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def setup_module(module):
    LogInit().set_logging(
                location='logs/',
                filename='musicfile_tests.log',
                debug=True,
                console=True)

class TestTags(unittest.TestCase):

    props = [
        'genre',
        'tracktotal',
        'tracknumber',
        'picture',
        'comment',
        'title',
        'grouping',
        'artist',
        'year',
        'albumartist',
        'disctotal',
        'discnumber',
        'composer',
        'album'
    ]

    def test_get_tags(self):
        props = Tags.get_tags()
        self.assertEqual(len(props),len(self.props))
        for p in self.props:
            self.assertIn(p,props)

class TestMusicTrack(unittest.TestCase):

    def test_get_track(self):
        with LogCapture() as l:
            m = MusicTrack()
            m.get_track()
            l.check(('Rkive.MusicFile','CRITICAL',"Method get_track not implemented"))

    def test_save(self):
        with LogCapture() as l:
            m = MusicTrack()
            m.save()
            l.check(('Rkive.MusicFile','CRITICAL',"Method save not implemented"))

class TestMP3(unittest.TestCase):
    pass

class TestFLAC(unittest.TestCase):
    pass

class TestMusicFile(unittest.TestCase):
    pass
