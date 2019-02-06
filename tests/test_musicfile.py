import unittest
import os.path
import logging
import string
import random
import shutil
import tempfile
from testfixtures import LogCapture as LogCapture
from logging import getLogger as getLogger
from rkive.clients.log import LogInit
from rkive.index.musicfile import MusicTrack, MP3, MusicTags


def str_generator(
        size=random.randrange(0, 101, 2),
        chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def setup_module(module):
    x = LogInit()
    x.quiet = False
    x.level = logging.DEBUG
    x.logger = 'logs/musicfile_tests.log'


class TestMusicTags(unittest.TestCase):

    def test_title(self):
        t = MusicTags()
        t.title = "XXXX"
        self.assertEquals(t.title, "XXXX")

    def test_tracktotal(self):
        t = MusicTags()
        t.tracktotal = 12
        self.assertEquals(t.tracktotal, 12)

    def test_tracknumber(self):
        t = MusicTags()
        t.tracknumber = 10
        self.assertEquals(t.tracknumber, 10)

    def test_album(self):
        t = MusicTags()
        t.album = "YYY"
        self.assertEquals(t.album, "YYY")

    def test_disctotal(self):
        t = MusicTags()
        t.disctotal = 12
        self.assertEquals(t.disctotal, 12)

    def test_discnumber(self):
        t = MusicTags()
        t.discnumber = 12
        self.assertEquals(t.discnumber, 12)

    def test_year(self):
        t = MusicTags()
        t.year = 1912
        self.assertEquals(t.year, 1912)

    def test_grouping(self):
        t = MusicTags()
        t.grouping = "Yellow"
        self.assertEquals(t.grouping, "Yellow")


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
        'album',
        'lyricist',
        'part'
    ]

    def test_get_tags(self):
        props = MusicTrack.get_rkive_tags()
        self.assertEqual(len(props), len(self.props))
        for p in self.props:
            self.assertIn(p, props)

    def test_save(self):
        e = ['CRITICAL:Rkive.MusicFile:Method save not implemented']
        with self.assertLogs('Rkive', level='DEBUG') as cm:
            m = MusicTrack()
            m.save()
            self.assertEqual(cm.output, e)


class TestID3(unittest.TestCase):

    def test_tracktotal(self):
        m = MP3()
        m.title = 'kkkk'
        m.tracknumber = "3"
        m.tracktotal = "5"
        self.assertEqual(m.tracknumber, "3")
        self.assertEqual(m.tracktotal, "5")


class TestMP3(unittest.TestCase):

    def setUp(self):
        log = getLogger('Rkive.MusicFile.Tests')
        self.tmpdir = tempfile.mkdtemp()
        self.tmpfile = os.path.join(self.tmpdir, 'test1.mp3')
        log.debug("Creating file for testing: {0}".format(self.tmpfile))
        shutil.copy('data/mp3/test1.mp3', self.tmpfile)

    def test_add_frames_to_empty_mp3(self):
        m = MP3()
        with LogCapture() as x:
            m.track = self.tmpfile
            r = 'Rkive.MusicFile'
            debug = 'DEBUG'
            l1 = (r, debug, f'Return file: {self.tmpfile}')
            x.check(l1)

    def test_set_all_params(self):
        m = MP3()
        m.track = self.tmpfile
        genre = str_generator()
        m.genre = genre
        tracktotal = "10"
        m.tracktotal = tracktotal
        tracknumber = "5"
        m.tracknumber = tracknumber
        comment = str_generator()
        m.comment = comment
        title = str_generator()
        m['title'] = title
        grouping = str_generator()
        m['grouping'] = grouping
        artist = str_generator()
        m['artist'] = artist
        year = "1910"
        m['year'] = year
        albumartist = str_generator()
        m['albumartist'] = albumartist
        disctotal = "11"
        m['disctotal'] = disctotal
        discnumber = "4"
        m['discnumber'] = discnumber
        composer = str_generator()
        m['composer'] = composer
        album = str_generator()
        m['album'] = album
        m.save()
        t = m.track
        id3vars = dict(t)
        for rkivetag, id3tag in dict(MP3.__dict__).items():
            if id3tag not in id3vars:
                continue
            id3val = str(id3vars[id3tag])
            if rkivetag == 'tracktotal':
                tracknumber, tracktotal = str(id3vars['TRCK']).split('/')
                self.assertEqual(tracktotal, "10")
                continue
            if rkivetag == 'tracknumber':
                tracknumber, tracktotal = str(id3vars['TRCK']).split('/')
                self.assertEqual(tracknumber, "5")
                continue
            if rkivetag == 'disctotal':
                discnumber, disctotal = str(id3vars['TPOS']).split('/')
                self.assertEqual(disctotal, "11")
                continue
            if rkivetag == 'discnumber':
                discnumber, disctotal = str(id3vars['TPOS']).split('/')
                self.assertEqual(discnumber, "4")
                continue
            rkiveval = m[rkivetag]
            self.assertEqual(id3val, rkiveval)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


class TestFLAC(unittest.TestCase):
    """ This to contain tests specific to FLAC files"""


class TestMusicFile(unittest.TestCase):
    """This to contain tests for the class MusicFile """
