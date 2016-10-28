import unittest
import sys
import os.path
import logging
import string
import random
import shutil
import tempfile
from testfixtures import LogCapture as LogCapture
from logging import getLogger as getLogger
from rkive.clients.log import LogInit
from rkive.index.musicfile import MusicTrack, Tags, MP3

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

class TestID3(unittest.TestCase):

    def test_get_id3_number(self):
        m=MP3('kkkk')
        val=m.get_id3_number("3","4")
        self.assertEqual(val,"4")
        val=m.get_id3_number("3/10","5")
        self.assertEqual(val,"5/10")

    def test_get_id3_total(self):
        m=MP3('kkkk')
        val=m.get_id3_total("5","10")
        self.assertEqual("5/10",val)
        val=m.get_id3_total("5/7","8")
        self.assertEqual("5/8",val)

class TestMP3(unittest.TestCase):

    def setUp(self):
        log = getLogger('Rkive.MusicFile.Tests')
        self.tmpdir=tempfile.mkdtemp()
        self.tmpfile=os.path.join(self.tmpdir,'test1.mp3')
        log.debug("Creating file for testing: {0}".format(self.tmpfile))
        shutil.copy('data/mp3/test1.mp3',self.tmpfile)

    def test_add_frames_to_empty_mp3(self):
        m=MP3(self.tmpfile)
        self.assertEqual(self.tmpfile,m.filename)
        with LogCapture() as l:
            mp3=m.get_track()
            mp3=m.get_track()
            r='Rkive.MusicFile'
            debug='DEBUG'
            l1=(r,debug,'Adding default ID3 frame to {0}'.format(self.tmpfile))
            l2=(r,debug,'Return file: {0}'.format(self.tmpfile))
            l.check(l1,l2)
    
    def test_set_all_params(self):
        m=MP3(self.tmpfile)
        genre=str_generator()
        m['genre']=genre
        tracktotal="10"
        m['tracktotal']=tracktotal
        tracknumber="5"
        m['tracknumber']=tracknumber
        comment=str_generator()
        m['comment']=comment
        title=str_generator()
        m['title']=title
        grouping=str_generator()
        m['grouping']=grouping
        artist=str_generator()
        m['artist']=artist
        year="1910"
        m['year']=year
        albumartist=str_generator()
        m['albumartist']=albumartist
        disctotal="10"
        m['disctotal']=disctotal
        discnumber="4"
        m['discnumber']=discnumber
        composer=str_generator()
        m['composer']=composer
        album=str_generator()
        m['album']=album
        m.save() 
        t=get_track()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

class TestFLAC(unittest.TestCase):
    pass

class TestMusicFile(unittest.TestCase):
    pass
