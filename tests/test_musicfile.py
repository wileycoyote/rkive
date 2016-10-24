import unittest
from rkive.index.musicfile import MusicTrack,Tag,ID3Tag
import sys
import logging
import string
import random

def str_generator(size=random.randrange(0, 101, 2), chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

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
    def test_get_properties(self):
        props = MusicTrack.get_properties()
        self.assertEqual(len(props),len(self.props))
        for p in self.props:
            self.assertIn(p,props)

    def test_set_genre(self):
        m=MusicTrack()
        genre=str_generator()
        m.genre=genre
        self.assertEqual(m.genre.value,genre)
        self.assertEqual(m.genre.name,'genre')

    def test_set_tracktotal(self):
        m=MusicTrack()
        tracktotal=12
        m.tracktotal=tracktotal
        self.assertEqual(m.tracktotal.value,tracktotal)
        self.assertEqual(m.tracktotal.name,'tracktotal')

    def test_set_tracknumber(self):
        m=MusicTrack()
        tracknumber=5
        m.tracknumber=tracknumber
        self.assertEqual(m.tracknumber.value,tracknumber)
        self.assertEqual(m.tracknumber.name,'tracknumber')

    def test_set_picture(self):
        m=MusicTrack()
        picture=str_generator()
        m.picture=picture
        self.assertEqual(m.picture.value,picture)
        self.assertEqual(m.picture.name,'picture')

    def test_set_comment(self):
        m=MusicTrack()
        comment=str_generator()
        m.comment=comment
        self.assertEqual(m.comment.value,comment)
        self.assertEqual(m.comment.name,'comment')

    def test_set_title(self):
        m=MusicTrack()
        title=str_generator()
        m.title=title
        self.assertEqual(m.title.value,title)
        self.assertEqual(m.title.name,'title')

    def test_set_grouping(self):
        m=MusicTrack()
        grouping=str_generator()
        m.grouping=grouping
        self.assertEqual(m.grouping.value,grouping)
        self.assertEqual(m.grouping.name,'grouping')

    def test_set_artist(self):
        m=MusicTrack()
        artist=str_generator()
        m.artist=artist
        self.assertEqual(m.artist.value,artist)
        self.assertEqual(m.artist.name,'artist')   

    def test_set_year(self):
        m=MusicTrack()
        year=str_generator(size=4)
        m.year=year
        self.assertEqual(m.year.value,year)
        self.assertEqual(m.year.name,'year')   

    def test_set_albumartist(self):
        m=MusicTrack()
        albumartist=str_generator()
        m.albumartist=albumartist
        self.assertEqual(m.albumartist.value,albumartist)
        self.assertEqual(m.albumartist.name,'albumartist')   

    def test_set_disctotal(self):
        m=MusicTrack()
        disctotal=10
        m.disctotal=disctotal
        self.assertEqual(m.disctotal.value,disctotal)
        self.assertEqual(m.disctotal.name,'disctotal')   

    def test_set_discnumber(self):
        m=MusicTrack()
        discnumber=5
        m.discnumber=discnumber
        self.assertEqual(m.discnumber.value,discnumber)
        self.assertEqual(m.discnumber.name,'discnumber')   

    def test_set_composer(self):
        m=MusicTrack()
        composer=str_generator()
        m.composer=composer
        self.assertEqual(m.composer.value,composer)
        self.assertEqual(m.composer.name,'composer')   


    def test_set_album(self):
        m=MusicTrack()
        album=str_generator()
        m.album=album
        self.assertEqual(m.album.value,album)
        self.assertEqual(m.album.name,'album')   

