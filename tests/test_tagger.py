import unittest
from rkive.clients.cl.tagger import Tagger as Tagger
from rkive.index.musicfile import MusicFile
import sys
import logging
import os.path
from rkive.clients.log import LogInit

class Dummy(object):
    pass

def setup_module(module):
    LogInit().set_logging(
            location='logs/',
            filename='tagger_tests.log',
            debug=True,
            console=True)

class TestTagger(unittest.TestCase):

    def test_musicfile_setup(self):
        d = Dummy()
        setattr(d,'tracknumber','1')
        setattr(d, 'artist', 'Cheeze Cheezely')
        setattr(d, 'title', 'A long way from home')
        setattr(d, 'album', 'Songs for the lonely')

    def test_set_tracks_from_markdown(self):
        log = logging.getLogger('Rkive.TestTagger')
        filename='data/markdown_test.txt'
        t=Tagger()
        t.set_tracks_from_markdown(filename)
        tracks = t._tracks
        #t.dump_tracks()
        self.assertEqual(len(tracks.keys()),55)
        self.assertEqual(tracks[0]['tracknumber'],"1")
        self.assertEqual(tracks[42]['artist'],"Orchestre de Paris - Pierre Dervaux")
