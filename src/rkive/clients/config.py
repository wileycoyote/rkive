from yaml import load
import os.path
import logging

class NoSourcesError(Exception):
    """ Exception to be raised when no configuration data for sources found
    """

class NoConnectionsError(Exception):
    """ Exception to be raised when no configuration data for connections found
    """

class Config:
    """Reads config files for source directories and db connection info

    Attributes:
        home: directory where config files are to be found
    """
    def __init__(self, home):
        self.sources = {}
        self.connections = []
        self.local_connections = []
        self.remote_connections = []
        self.home = home

    def read_sources(self):
        """ read source file from designated folder
            throw exceptions for no file found, or no data
        """
        source = os.path.join(self.home, 'sources.yml')
        try:
            with open(source) as s:
                d = load(s)
                if d is None:
                    raise NoSourcesError
                if not isinstance(d,dict):
                    raise NoSourcesError
                for k, v in d.items():
                    reverse_key = v.lower()
                    if not reverse_key in self.sources:
                        self.sources[reverse_key] = []
                    self.sources[reverse_key].append(k)
        except EnvironmentError:
            raise EnvironmentError
        if self.sources == {}:
            raise NoSourcesError
        return True

    def read_connections(self):
        conns_cfg = os.path.join(self.home, 'connections.yml')
        print(conns_cfg)
        try:
            with open(conns_cfg) as cf:
                conns = load(cf)
                if conns is None:
                    raise NoConnectionsError
                if not isinstance(conns,list):
                    raise NoConnectionsError
                for conn in conns:
                    print(conn)
                    # Test for must have parameters first
                    if not 'type' in conn:
                        raise NoConnectionsError
                    if not 'path' in conn:
                        raise NoConnectionsError
                    if not 'status' in conn:
                        raise NoConnectionsError
                    if not 'location' in conn:
                        raise NoConnectionsError
                    dbtype = conn['type']
                    path=conn['path']
                    location=conn['location']
                    status=conn['status']
                    username = ''
                    if 'username' in conn:
                        username = conn['username']
                    password = ''
                    if 'password' in conn:
                        password = ':'+conn['password']+'@'
                    host = ''
                    if 'host' in conn:
                        host = conn['host']
                    port = ''
                    if 'port' in conn:
                        port = ':'+conn['port']
                    url='{0}://{1}{2}{3}{4}/{5}'.format(dbtype,username,password,host,port,path)
                    self.connections.append((status, location, url))
        except EnvironmentError:
            raise EnvironmentError
        if not self.connections:
            raise NoConnectionsError
        return True

    def get_music(self):
        if not "music" in self.sources:
            return None

    def get_movies(self):
        if not "movies" in self.sources:
            return None
        return self.sources["movies"]

    def get_local_live_connections(self):
        return([c[2] for c in self.connections if 'live' in c[0] and 'local' in c[1]])

    def get_remote_live_connections(self):
        return ([c[2] for c in self.connections if 'live' in c[0] and 'remote' in c[1]])

    def get_all_connections(self):
        return self.connections
