import unittest
from rkive.index.musicfile import MusicTrack,Tag,ID3Tag
import sys
import logging

class TestTag(unittest.TestCase):

    def test_set_property_in_constructor(self):
        t = Tag(name='name',value='value') 
        self.assertEqual(t.name,"name")
        self.assertEqual(t.value,"value")

    def test_property_setters(self):
        t = Tag()
        t.name='title'
        t.value='value'
        self.assertEqual(t.name,"title")
        self.assertEqual(t.value,"value")


class TestID3Tag(unittest.TestCase):

    def test_set_property(self):
        t=ID3Tag()
        t.id3name='TIT2'
        self.assertEqual(t.id3name, 'TIT2')
        self.assertTrue(callable(t.func))

class TestMusicTrack(unittest.TestCase):
    props = [
        'genre',
        'tracktotal',
        'picture',
        'comment',
        'title',
        'grouping',
        'artist',
        'year',
        'tracknumber',
        'albumartist',
        'disctotal',
        'discnumber',
        'composer',
        'album'
    ]
    def test_get_properties(self):
        props = MusicTrack.get_properties()
        self.assertEqual(len(props),len(self.props))
        for p in self.props:
            self.assertIn(p,props)

    def test_title_property(self):
        m = MusicTrack()
        m.title ='XXXXXXX'
        self.assertEqual(m.title.value,'XXXXXXX')
        self.assertEqual(m.title.name,'title')

    def test_album_property(self):
        m = MusicTrack()
        m.album ='XXXXXXX'
        self.assertEqual(m.album.value,'XXXXXXX')
        self.assertEqual(m.album.name,'album')
