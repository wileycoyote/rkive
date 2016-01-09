from logging import getLogger
import paramiko
import os
from rkive.uploader.net.common import NetworkCodes as netcode

class NetworkClient(object):

    def get_size_of_partition(self, partition):
        log = getLogger('Rkive.NetworkClient')
        log.fatal("get_size_of_partition not implemented")
    
    def get_host(self):
        log = getLogger('Rkive.NetworkClient')
        log.fatal("get_host not implemented")

    def get(self):
        log = getLogger('Rkive.NetworkClient')
        log.fatal("get not implemented")

    def put(self):
        log = getLogger('Rkive.NetworkClient')
        log.fatal("put not implemented")

    def mkdir(self):
        log = getLogger('Rkive.NetworkClient')
        log.fatal("mkdir not implemented")

class SFTP(NetworkClient):

    conn = None
    sftp = None

    def __init__(self, ipaddress, username):
        self.ipaddress = ipaddress
        self.username = username

    def connect(self):
        if (self.conn):
            return self.conn
        self.conn = paramiko.SSHClient()
        self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.conn.connect(self.ipaddress, username=self.username) 
        self.sftp = self.conn.open_sftp()
        return self.sftp

    def get_size_of_partition(self, partition):
        self.connect()
        stdin, stdout, stderr = self.conn.exec_command("df -k")
        for line in stdout.readlines():
            l = line.strip()
            if (l.startswith(partition)):
                s = re.split('\s+', l)[2]
                return s

    def mkdir(self, d):
        sftp = self.connect()
        sftp.mkdir(d)
        
import socket

class SocketClient(NetworkClient):

    conn = None

    def __init__(self, ipaddress, port, username=None):
        self.ipaddress = ipaddress
        self.port = port

    def connect(self):
        log = getLogger('Rkive.TransceiverClient')
        if (self.conn != None):
            return
        # SOCK_DGRAM is the socket type to use for UDP sockets
        log.info("ipaddress: {0} port: {1}".format(self.ipaddress, self.port))
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.ipaddress, self.port))
        return self.conn

    def close(self):
        self.conn.close()
        self.conn = None

    def fin(self):
        try:
            conn = self.connect()
            data = "{0}\n".format(netcode.FIN)
            conn.sendall(data)
        finally:
            self.close()

    def get_partition_size(self, partition):
        size = 0
        try:
            conn = self.connect()
            data = "{0}\n{1}\n".format(netcode.SZE, partition)
            conn.sendall(data)
            size = conn.recv(1024)
        finally:
            self.close()
        return size

    def mkdir(self, d):
        log = getLogger('Rkive.TransceiverClient')
        try:
            conn = self.connect()
            data = "{0}\n{1}\n".format(netcode.MKD, d)
            conn.sendall(data)
            status = conn.recv(1024)
            if (status != netcode.AOK):
                log.fatal("Failure to create {0}".format(d))
        finally:
            self.close()

    def put(self, s, t):
        log = getLogger('Rkive.TransceiverClient')
        try:
            conn = self.connect()
            data = "{0}\n{1}\n".format(netcode.PUT, t)
            conn.sendall(data)
            log.info(data)
            with open(s,"rb") as fh:
                buf = fh.read(netcode.MAXBUF)
                while buf != "":
                    # Do stuff with byte.
                    conn.sendall(buf)
                    buf = fh.read(netcode.MAXBUF)
                conn.sendall(netcode.EOF)
            ack = conn.recv(3)
            if (ack != netcode.AOK):
                log.fatal("Problem with sending file {0}".format(ack))
        finally:
            self.close()

    def get(self, src, tgt):
        log = getLogger('Rkive.TransceiverClient')
        try:
            conn = self.connect()
            data = "{0}\n{1}\n".format(netcode.GET, src)
            log.info("data: {0}".format(data))
            conn.sendall(data)
            with open(tgt, "wb") as fh:
                while(1):
                    buf = conn.recv(netcode.MAXBUF)
                    if (buf == netcode.EOF): 
                        log.info("Finished download")
                        break
                    fh.write(buf)
        finally:
            log.info("close connection")
            self.close()

    def ack(self):
        log = getLogger('Rkive.TransceiverClient')
        status = False
        try:
            conn = self.connect()
            data = "{0}\n".format(netcode.ACK)
            log.info( "DATA: {0}".format(data))
            conn.sendall(data)
            aok = conn.recv(1024)
            log.info("return: {0}".format(aok))
            if (aok != netcode.AOK):
                log.fatal("Failure to establish connection")
            else:
                status = True
        finally:
            log.info("close connection")
            self.close()
        log.info("close connection {0}".format(status))
        return status

class UploadClient(SocketClient):
    pass
