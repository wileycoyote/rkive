from yaml import load as yaml_load
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
        connections: path for connections file
        sources: path for sources file
    """
    def __init__(self,sources_cfg="",connections_cfg=""):
        self._connections_cfg = ""
        self._sources_cfg = ""
        self._sources = {}
        self._connections = []
        if sources_cfg:
            self.sources=sources_cfg
        if connections_cfg:
            self.connections=connections_cfg

    @property
    def sources(self):
        return self._sources

    @sources.setter
    def sources(self, source_cfg):
        if self._sources:
            return self._sources
        if os.path.isdir(source_cfg):
            self._sources={}
            return
        try:
            with open(source_cfg) as s:
                d = yaml_load(s)
                if d is None:
                    print("No sources in file")
                    raise NoSourcesError
                if not isinstance(d,dict):
                    print("Isnt a dictionary "+d)
                    raise NoSourcesError
                for source_folder, source_category in d.items():
                    source_category = source_category.lower()
                    if not source_folder in self._sources:
                        self._sources[source_category] = []
                    self._sources[source_category].append(source_folder)
        except EnvironmentError:
            self._sources={} 
        except NoSourcesError:
            self._sources={} 

    @property
    def connections(self):
        return self._connections

    @connections.setter
    def connections(self, connections_cfg):
        if self._connections:
            return 
        if os.path.isdir(connections_cfg):
            self._connections={}
            return
        try:
            print(connections_cfg)
            with open(connections_cfg) as cf:
                conns = yaml_load(cf)
                if conns is None:
                    raise NoConnectionsError
                if not isinstance(conns,list):
                    raise NoConnectionsError
                for conn in conns:
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
                    if not os.path.isfile(path):
                        fh=open(path,'w')
                        fh.close()
                    self._connections.append((status, location, url))
        except EnvironmentError as e:
            print("Environment ERror "+str(e))
            self._connections={}
            return
        except NoConnectionsError:
            print("No connections")
            self._connections={}
            return 

    def get_music(self):
        if not "music" in self._sources:
            return None
        return self._sources["music"]

    def get_movies(self):
        if not "movies" in self._sources:
            return None
        return self._sources["movies"]

    @property
    def local_live_connections(self):
        return([c[2] for c in self._connections if 'live' in c[0] and 'local' in c[1]])

    @property 
    def remote_live_connections(self):
        return ([c[2] for c in self._connections if 'live' in c[0] and 'remote' in c[1]])
