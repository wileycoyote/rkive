import unittest
from rkive.index.musicfile import MusicTrack,Tag,ID3Tag
import sys
import logging

class TestTag(unittest.TestCase):

    def test_set_property_in_constructor(self):
        t = Tag()
        t.name='title'
        t.value='value'
        self.assertEqual(t.name,"title")
        self.assertEqual(t.value,"value")

class TestID3Tag(unittest.TestCase):
    pass

class TestMusicTrack(unittest.TestCase):
    pass
