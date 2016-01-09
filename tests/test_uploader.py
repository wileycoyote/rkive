import unittest
import sys
import os
import os.path
import shutil 
import threading
from logging import getLogger
from rkive.uploader.client import UploadManager
from rkive.uploader.net.server import UploadServer
from unittest.mock import patch

local =  os.path.join(os.getcwd(), 'tmp', 'local')
remote = os.path.join(os.getcwd(),'tmp','remote')
class MockManager:
    folders = {
        'Music' : {'local':local, 'remote': remote}
    }


class TestUploader(unittest.TestCase):
    
    @patch ('rkive.uploader.config.ConfigManager')    
    def setUp(self, MockManager):
        m = MockManager()
        m.set_host('local')
        m.make_empty_base()
        self.conn = UploadManager()

        m.set_host('remote')
        m.make_empty_base()
        server = UploadServer(('localhost', 0), UploadRequestReHandler)
        ip, port = server.server_address
        server.serve_forever()
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        self.server = server

    def tearDown(self):
        self.server.shutdown()
        shutil.rmtree(remote)
        shutil.rmtree(local)

    def test_upload_file_to_server(self, MockManager):
        log = getLogger('Rkive.Tests')
        #add a few files
        data = 'data/mp3'
        files = os.listdir(data)
        tgt = os.path.join(local, 'Music', 'Album_Name')
        os.makedirs(tgt)
        for f in files:
            src = os.path.join(data, f)
            shutil.copy(src,tgt)     
        self.conn.upload_files() 
        # check that files exist
        files = os.listdir('data/mp3')
        remote_fp = os.path.join(remote, 'Music', 'Album_name')
        for f in files:
            fp = os.path.join(remote_fp, f)
            self.assertTrue(os.path.exists(fp), 
                "File path {0} does not exist".format(fp))

