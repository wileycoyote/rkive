#!/usr/bin/env python

import socket

class NetworkCodes(object):

    MAX_PACKET = 1024
    PUT = 'PUT'
    GET = 'GET'
    AOK = '400'
    ERR = '401' 
    SERVER_PORT = 9001
    FIN = 'FIN'


class TransceiverClient(NetworkCodes):

    conn = None

    def __init__(self, ipaddress, port, username=None):
        self.ipaddress = ipaddress
        self.port = port

    def connect(self):
        if (self.conn != None):
            return
        # SOCK_DGRAM is the socket type to use for UDP sockets
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.ipaddress, self.port))
        return self.conn

    def get_partition_size(self, partition):
        size = 0
        conn = None
        try:
            conn = self.connect()
            data = "{0}\n{1}\n".format(self.SZE, partition)
            conn.sendall(data)
            size = self.conn.recv(1024)
        finally:
            conn.close()
        return size

    def mkdir(self, d):
        log = getLogger('Rkive.TransceiverClient')
        conn = None
        try:
            conn = self.connect()
            data = "{0}\n{1}\n".format(self.MKD, d)
            conn.sendall(data)
            status = conn.recv(1024)
            if (status != self.AOK):
                log.fatal("Failure to create {0}".format(d))
        finally:
            conn.close()

    def put(self, f):
        log = getLogger('Rkive.TransceiverClient')
        conn = None
        try:
            conn = self.connect()
            size = os.path.getsize(f)
            data = "{0}\n{1}\n{2}\n".format(self.PUT, f, size)
            with open(f,"rb") as fh:
                buff = fh.read(1024)
                while byte != "":
                    # Do stuff with byte.
                    conn.sendall(buf)
                    buff = fh.read(1024)
        finally:
            conn.close()

    def get(self, tgt, src):
        log = getLogger('Rkive.TransceiverClient')
        conn = None
        try:
            conn = self.connect()
            data = "{0}\n{1}\n".format(self.GET, f)
            conn.sendall(data)
            size = int(conn.rfile.readline().strip())
            bytes_recvd = 0
            with open(src, "wb") as fh:
                while(bytes_recvd <= size):
                    buf = conn.recv(1024)
                    fh.write(buf)
                    bytes_recvd = bytes_recvd + len(buf) 
        finally:
            conn.close

    def fin(self):
        conn = None
        try:
            print "hello"
            conn = self.connect()
            data = "{0}\n".format(self.FIN)
            print "hello"
            conn.sendall(data)
            print "HEHEHEHE"
        finally:
            conn.close()


if (__name__ == '__main__'):
    c = TransceiverClient('localhost', 9000)
    c.fin()
