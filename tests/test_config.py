import unittest
from rkive.clients.config import Config as Config
import  tempfile

class TestGetConfig(unittest.TestCase):

    def test_no_sources(self):
        t =  tempfile.gettempdir()
        c = Config(t)
        self.assertFalse(c.read_sources())

    def test_no_connections(self):
        t =  tempfile.gettempdir()
        c = Config(t)
        self.assertFalse(c.read_connections())

    def test_sources(self):
        c = Config('data/config/')
        self.assertTrue(c.read_sources())

        m = c.get_music()
        self.assertIsNone(m)

        m = c.get_movies()
        self.assertIsNotNone(m)
        self.assertEquals(1,len(m))
        self.assertIn('/media/roger/Music/Collections',m)

    def test_connections(self):
        c = Config('data/config')
        c.read_connections()
        conns = c.get_live_connections()
        self.assertEquals(1,len(conns))
        url = ''
        self.assertIn(url, conns)

