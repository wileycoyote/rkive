import unittest
from rkive.clients.config import Config as Config

class TestGetConfig(unittest.TestCase):

    def test_sources(self):
        c = Config('data/config/')
        c.read()

        m = c.get_music()
        self.assertIsNone(m)

        m = c.get_movies()
        self.assertIsNotNone(m)
        self.assertEquals(1,len(m))
        self.assertIn('/media/roger/Music/Collections',m)

    def test_connections(self):
        c = Config('data/config')
        c.read()
        conns = c.get_live_connections()
        self.assertIsNone(conns)
        self.assertEquals(1,len(conns))
        url = ''
        self.assertIn(url, conns)

