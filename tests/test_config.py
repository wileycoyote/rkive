import unittest
from rkive.clients.config import Config as Config
from rkive.clients.config import NoSourcesError as NoSourcesError
from rkive.clients.config import NoConnectionsError as NoConnectionsError
import  tempfile
import os, os.path

class TestGetConfig(unittest.TestCase):

    def test_no_sources(self):
        t =  tempfile.gettempdir()
        c = Config(t)
        self.assertRaises(NoSourcesError, c.read_sources)

    def test_empty_source_file(self):
        t = tempfile.gettempdir()
        fp = os.path.join(t, 'sources.yml')
        open(fp,'w')
        c = Config(t)
        self.assertRaises(NoSourcesError, c.read_sources)

    def test_no_connections(self):
        t =  tempfile.gettempdir()
        c = Config(t)
        self.assertRaises(NoConnectionsError, c.read_connections)

    def test_empty_connections_file(self):
        t = tempfile.gettempdir()
        c = Config(t)
        fp = os.path.join(t, 'connections.yml')
        open(fp, 'w')
        self.assertRaises(NoConnectionsError, c.read_connections)

    def test_connection_file_with_rubbish_content(self):
        t = tempfile.gettempdir()
        c = Config(t)
        fp = os.path.join(t, 'connections.yml')
        with open(fp, 'w') as f:
            f.write("ldkfsalkknlvkn")
        self.assertRaises(NoConnectionsError, c.read_connections)

    def test_source_file_with_rubbish_content(self):
        t = tempfile.gettempdir()
        c = Config(t)
        fp = os.path.join(t, 'sources.yml')
        with open(fp, 'w') as f:
            f.write("ldkfsalkknlvkn")
        self.assertRaises(NoSourcesError, c.read_sources)

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
        url = 'sqlite3:///tests/data/config/rkive/database'
        self.assertIn(url, conns)

