import unittest
from rkive.clients.config import Config as Config
from rkive.clients.config import NoSourcesError as NoSourcesError
from rkive.clients.config import NoConnectionsError as NoConnectionsError
import  tempfile
import os, os.path
from logging import getLogger as getLogger
from rkive.clients.log import LogInit

class TestGetConfig(unittest.TestCase):

    def setup_module(self):
        LogInit().set_logging(
            location='logs/',
            filename='config_tests.log',
            debug=True,
            console=True)

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
        music = c.music
        print(music)
        self.assertIsNotNone(music)
        self.assertEquals(1,len(music))
        self.assertIn('/media/roger/Music/Collections',music)
        movies = c.movies
        self.assertIsNone(movies)

    def test_live_connections(self):
        c = Config()
        c.connections='data/config/connections.yml'
        local_conns = c.local_live_connections
        self.assertEquals(1,len(local_conns))
        url = 'sqlite3:///data/config/database.db'
        self.assertIn(url, local_conns)
        remote_connections = c.remote_live_connections
        self.assertEquals(0, len(remote_connections))

    def test_multiple_live_connections(self):
        pass
