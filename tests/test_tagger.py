import unittest
from rkive.clients.cl.tagger import Tagger
from rkive.index.musicfile import Media, MusicFile
import sys
import logging
import os.path

class Dummy(object):
    pass

class TestTagger(unittest.TestCase):

    def test_musicfile_setup(self):
        d = Dummy()
        setattr(d,'tracknumber','1')
        setattr(d, 'artist', 'Cheeze Cheezely')
        setattr(d, 'title', 'A long way from home')
        setattr(d, 'album', 'Songs for the lonely')
