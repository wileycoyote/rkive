import unittest
import os
import shutil
from  rkive.clients.log import LogInit
import sys
import logging
import threading
from rkive.uploader.net.clients import SocketClient
from rkive.uploader.net.server import UploadServer, UploadRequestHandler

class TestTxSocketServer(unittest.TestCase):

    tests_dir = '/tmp/rkive'

    def setUp(self):
        LogInit().set_logging(location='logs', filename='test.log', debug=True, console=True)
        log = logging.getLogger('Rkive')
        log.info("START")
        # Port 0 means to select an arbitrary unused port
        HOST, PORT = "localhost", 0

        server = UploadServer((HOST, PORT), UploadRequestHandler)
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        self.client = SocketClient(ip, port)
        self.server = server
        cwd = os.getcwd()
        self.tests_dir = cwd+self.tests_dir
        os.makedirs(self.tests_dir)
        os.chdir(cwd)
        log.info("test_ack_server")
 
    def tearDown(self):
        log = logging.getLogger('Rkive')
        log.info("Teardown")        
        shutil.rmtree(self.tests_dir)
        self.server.shutdown()

    def test_ack_server(self):
        log = logging.getLogger('Rkive')
        log.info("test_ack_server")
        r = self.client.ack()
        self.assertTrue(r, "Server Acknowledgement is good")
    
    def test_get_file(self):
        log = logging.getLogger('Rkive')
        s = os.getcwd()+'/data/mp3/01-Johnny Strikes Up the Band.mp3'
        t = self.tests_dir+'/t.mp3' 
        log.info( "transferring "+s)
        log.info( "to "+t)
        self.client.get(s,t)
        self.assertTrue(os.path.exists(t), "File has been transferred")

    def test_put_file(self):
        s = os.getcwd()+'/data/mp3/01-Johnny Strikes Up the Band.mp3'
        t = self.tests_dir+'/t.mp3' 
        self.client.put(s, t)
        self.assertTrue(os.path.exists(t), "File has been transferred")


