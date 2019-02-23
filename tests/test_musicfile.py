import unittest
import os.path
import logging
import string
import random
import shutil
import tempfile
from logging import getLogger as getLogger
from rkive.clients.log import LogInit
from rkive.index.musicfile import MusicTrack, MP3, MusicTags
from rkive.index.musicfile import Flac


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


class TestMP3(unittest.TestCase):

    def setUp(self):
        log = getLogger('Rkive.MusicFile.Tests')
        self.tmpdir = tempfile.mkdtemp()
        self.tmpfile = os.path.join(self.tmpdir, 'test1.mp3')
        log.debug("Creating file for testing: {0}".format(self.tmpfile))
        shutil.copy('data/mp3/test1.mp3', self.tmpfile)

    def test_set_all_params(self):
        m = MP3()
        m.media = self.tmpfile
        attrs = {}
        genre = str_generator()
        m.genre = genre
        attrs['genre'] = genre

        tracktotal = "10"
        m.tracktotal = tracktotal
        attrs['tracktotal'] = tracktotal

        tracknumber = "5"
        m.tracknumber = tracknumber
        attrs['tracknumber'] = tracknumber

        comment = str_generator()
        m.comment = comment
        attrs['comment'] = comment

        title = str_generator()
        m.title = title
        attrs['title'] = title

        grouping = str_generator()
        m.grouping = grouping
        attrs['grouping'] = grouping

        artist = str_generator()
        m.artist = artist
        attrs['artist'] = artist

        year = "1910"
        m.year = year
        attrs['year'] = year

        albumartist = str_generator()
        m.albumartist = albumartist
        attrs['albumartist'] = albumartist

        disctotal = "11"
        m.disctotal = disctotal
        attrs['disctotal'] = disctotal

        discnumber = "4"
        m.discnumber = discnumber
        attrs['discnumber'] = discnumber

        composer = str_generator()
        m.composer = composer
        attrs['composer'] = composer

        album = str_generator()
        m.album = album
        attrs['album'] = album

        m.save()
        test_all = False
        for rkivetag in MusicTrack.get_rkive_tags():
            if not hasattr(m, rkivetag):
                continue
            a = getattr(m, rkivetag)
            test_all = True
            if rkivetag in attrs:
                self.assertEquals(a, attrs[rkivetag])
        self.assertTrue(test_all, "We've not tested any attribute")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


class TestFLAC(unittest.TestCase):
    """ This to contain tests specific to FLAC files"""

    def setUp(self):
        log = getLogger('Rkive.MusicFile.Tests')
        self.tmpdir = tempfile.mkdtemp()
        self.tmpfile = os.path.join(self.tmpdir, 'test1.flac')
        log.debug("Creating file for testing: {0}".format(self.tmpfile))
        shutil.copy('data/flac/test.flac', self.tmpfile)

    def test_set_all_params(self):
        m = Flac()
        m.media = self.tmpfile
        attrs = {}

        genre = str_generator()
        m.genre = genre
        attrs['genre'] = genre

        tracktotal = "10"
        m.tracktotal = tracktotal
        attrs['tracktotal'] = tracktotal

        tracknumber = "5"
        m.tracknumber = tracknumber
        attrs['tracknumber'] = tracknumber

        comment = str_generator()
        m.comment = comment
        attrs['comment'] = comment

        title = str_generator()
        m.title = title
        attrs['title'] = title

        grouping = str_generator()
        m.grouping = grouping
        attrs['grouping'] = grouping

        artist = str_generator()
        m.artist = artist
        attrs['artist'] = artist

        year = "1910"
        m.year = year
        attrs['year'] = year

        albumartist = str_generator()
        m.albumartist = albumartist
        attrs['albumartist'] = albumartist

        disctotal = "11"
        m.disctotal = disctotal
        attrs['disctotal'] = disctotal

        discnumber = "4"
        m.discnumber = discnumber
        attrs['discnumber'] = discnumber

        composer = str_generator()
        m.composer = composer
        attrs['composer'] = composer

        album = str_generator()
        m.album = album
        attrs['album'] = album

        m.save()
        for t in MusicTrack.get_rkive_tags():
            if hasattr(m, t):
                a = getattr(m, t)
                test_val = attrs[t]
                self.assertEquals(a, test_val)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


class TestMusicFile(unittest.TestCase):
    """This to contain tests for the class MusicFile """
