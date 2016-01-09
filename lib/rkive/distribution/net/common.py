class PathNotFound(Exception):
    pass

class NoSuchFunction(Exception):
    pass

class NetworkCodes(object):

    MAX_PACKET = 1024
    PUT = 'PUT'
    GET = 'GET'
    AOK = '400'
    ERR = '401' 
    SERVER_PORT = 9001
    FIN = 'FIN'
    ACK = '500'
    MKD = 'MKD'
    SZE = 'SZE'
    MAXBUF = 1024
    EOF    = '-1'
