from logging import getLogger
from rkive.uploader.net.common import NetworkCodes as netcode
from rkive.uploader.net.common import PathNotFound, NoSuchFunction
import rkive.uploader.config
import os
import select
import socket

import SocketServer

class UploadRequestHandler(SocketServer.BaseRequestHandler):

    HOST = 'localhost'
    
    def get_partition_size(self, partition):
        partition = self.rfile.readline().strip()
        size = 1
        self.request.sendall(size)

    def put(self):
        log = getLogger('Rkive.UploadRequestHandler')
        fn = self.rfile.readline().strip()
        leafs, base = fn.rsplit('/', 1)
        if (not os.path.exists(leafs)):
            log.debug("Creating folder {0}".format(leafs))
            os.makedirs(leafs)
        with open(fn, "wb") as fh:
            while(1):
                buf = self.request.recv(netcode.MAXBUF)
                if (buf == netcode.EOF): 
                    log.info("Finished download")
                    break
                fh.write(buf)
        self.request.sendall(netcode.AOK)
        
    def get(self):
        log = getLogger('Rkive.UploadRequestHandler')
        fn = self.rfile.readline().strip()
        log.info("Filename {0}".format(fn))
        if (not os.path.exists(fn)):
            raise PathNotFound
        log.info("Filename {0}".format(fn))
        with open(fn,"rb") as fh:
            buf = fh.read(netcode.MAXBUF)
            while buf != "":
                # Do stuff with byte.
                self.request.sendall(buf)
                buf = fh.read(netcode.MAXBUF)
            self.request.sendall(netcode.EOF)

    def mkdir(self, d):
        log = getLogger('Rkive.UploadRequestHandler')
        d = self.request.rfile.readline().strip()
        parents = '/'.join(d.split('/')[0:-2])
        if (not os.path.exists(parents)):
            raise PathNotFound
        os.makedirs(d)

    def error(self):
        self.request.sendall(netcode.ERR)
        
    def ack(self):
        log = getLogger("Rkive.Server")
        log.info("function: ack")
        self.request.sendall(netcode.AOK)
 
    def handle(self):
        log = getLogger("Rkive.Server")
        log.info( "Start Server")
        Dispatcher = {
            netcode.MKD : self.mkdir,
            netcode.SZE : self.get_partition_size,
            netcode.PUT : self.put,
            netcode.GET : self.get,
            netcode.ACK : self.ack
        }
        u = UploadManager()
        u.make_all_folders()
        req = self.request.recv(3)
        log.info( "REQ: {0}".format(req))
        self.request.recv(1)
        try:
            if not req in Dispatcher:
                raise NoSuchFunction(req)
            Dispatcher[req]()
        except Exception as e:
            log.fatal("Error: {0}".format(e))
            self.request.sendall(netcode.ERR)

class UploadServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer): 
    pass
