import unittest
from rkive.clients.config import Config as Config
from rkive.clients.config import NoSourcesError as NoSourcesError
from rkive.clients.config import NoConnectionsError as NoConnectionsError
import  tempfile
import os, os.path

class TestGetConfig(unittest.TestCase):

    def test_no_sources(self):
        c = Config()
        c.sources=tempfile.gettempdir()
        self.assertEquals({}, c.sources)

    def test_empty_source_file(self):
        t = tempfile.gettempdir()
        fp = os.path.join(t, 'sources.yml')
        fh = open(fp,'w')
        fh.close()
        c = Config()
        c.sources=fp
        self.assertEquals({},c.sources)

    def test_no_connections(self):
        c = Config()
        c.connections=tempfile.gettempdir()
        self.assertEquals({}, c.connections)

    def test_empty_connections_file(self):
        t = tempfile.gettempdir()
        fp = os.path.join(t, 'connections.yml')
        fh=open(fp, 'w')
        fh.close() 
        c = Config()
        c.connections=fp
        self.assertEquals({}, c.connections)

    def test_connection_file_with_rubbish_content(self):
        t = tempfile.gettempdir()
        fp = os.path.join(t, 'connections.yml')
        with open(fp, 'w') as f:
            f.write("ldkfsalkknlvkn")
        c = Config()
        c.connections=fp
        self.assertEquals({},c.connections)

    def test_source_file_with_rubbish_content(self):
        t = tempfile.gettempdir()
        fp = os.path.join(t, 'sources.yml')
        with open(fp, 'w') as f:
            f.write("ldkfsalkknlvkn")
        c = Config()
        c.sources=fp
        self.assertEquals({}, c.sources)

    def test_sources(self):
        c = Config()
        c.sources='data/config/sources.yml'
        self.assertTrue(c.sources)
        m = c.get_music()
        self.assertIsNone(m)
        m = c.get_movies()
        self.assertIsNotNone(m)
        self.assertEquals(1,len(m))
        self.assertIn('/media/roger/Music/Collections',m)

    def test_live_connections(self):
        c = Config()
        c.connections='data/config/connections.yml'
        local_conns = c.local_live_connections
        self.assertEquals(1,len(local_conns))
        url = 'sqlite3:///data/config/database.db'
        self.assertIn(url, local_conns)
        remote_connections = c.remote_live_connections
        self.assertEquals(0, len(remote_connections))
