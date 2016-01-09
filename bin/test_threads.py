#!/usr/bin/env python
import socket
import select
import threading
import SocketServer
import sys

class NetworkCodes(object):

    MAX_PACKET = 1024
    PUT = 'PUT'
    GET = 'GET'
    AOK = '400'
    ERR = '401' 
    SERVER_PORT = 9001
    FIN = 'FIN'
    MKD = 'MKD'
    SZE = 'SZE'
    RCV = 'RCV'

class TransceiverHandler(SocketServer.BaseRequestHandler, NetworkCodes):

    HOST = 'localhost'

    def get_partition_size(self, partition):
        pass

    def put(self, url):
        (d, leaf) = os.path.split(url)
        if (not os.path.exists(d)):
            raise PathNotFound
                 
    def get(self, url):
       if (not os.path.exists(url)):
            raise PathNotFound
 
    def mkdir(self, d):
        log = getLogger('Rkive.TransceiverHandler')
        parents = '/'.join(d.split('/')[0:-2])
        if (not os.path.exists(parents)):
            raise PathNotFound
        os.mkdir(d)

    def handle(self):
        req = self.request.recv(3)
        print "XXXXXXXXXXX"
        print "REQ: "+req +" " +str(len(req))
        print self.FIN
        try:
            print "XXXXX"
            if (req == self.MKD):
                d = self.request.rfile.readline().strip()
                self.mkdir(d)
            if (req == self.SZE):
                partition = self.request.rfile.readline().strip()
                size = self.get_partition_size(partition)
                self.request.sendall(size)
            if (req == self.PUT):
                fn = self.request.rfile.readline().strip()
                size = self.request.rfile.readline().strip()
                self.put(fn, size)
            if (req == self.GET):
                fn = self.request.rfile.readline().strip()
                size = self.get()
                self.request.sendall(size)
            if (req == self.RCV):
                size = self.request.readline().strip()
                data = self.request.recv(self.MAX_PACKET)
                self.put(size, data)
            if (req == self.FIN):
                server.shutdown()
                server.__shutdown_request=True
            self.request.sendall(self.AOK)
        except Exception as e:
            print "Exception" +str(e)
            self.request.sendall(self.ERR)

class TransceiverServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    address_family = socket.AF_INET
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass):
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
        self.__is_shut_down = threading.Event()
        self.__shutdown_request = False
 
    def serve_forever(self, poll_interval=0.5):
        """provide an override that can be shutdown from a request handler.
        The threading code in the BaseSocketServer class prevented this from working
        even for a non-threaded blocking server.
        """
        self.__is_shut_down.clear()
        try:
            while not self.__shutdown_request:
                server = self.socket
                inputs = [server]
                outputs = []
                readable, writable, exceptional = select.select(inputs, outputs, inputs)
                for s in readable:
                    if s is server:
                        self._handle_request_noblock()
        finally:
            self.__shutdown_request = False
            self.__is_shut_down.set()

    def shutdown(self):
        """Stops the serve_forever loop.
 
         Blocks until the loop has finished. This must be called while
         serve_forever() is running in another thread, or it will
         deadlock.
        """
        self.__shutdown_request = True
        self.__is_shut_down.wait()
 
    def _handle_request_noblock(self):
        """Handle one request, without blocking.
 
         I assume that select.select has returned that the socket is
         readable before this function was called, so there should be
         no risk of blocking in get_request().
        """
        try:
             request, client_address = self.get_request()
        except socket.error:
            return
        if self.verify_request(request, client_address):
            try:
                self.process_request(request, client_address)
            except:
                self.handle_error(request, client_address)
                self.close_request(request)

if (__name__ == '__main__'):
    print "run"
    server = TransceiverServer(('localhost', 9000), TransceiverHandler)
    ip, port = server.server_address
    server.serve_forever()
    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name
