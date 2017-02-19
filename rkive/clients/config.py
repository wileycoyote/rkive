from yaml import load as yaml_load
import os.path
from logging import getLogger

class NoSourcesError(Exception):
    """ Exception to be raised when no configuration data for sources found
    """

class NoConnectionsError(Exception):
    """ Exception to be raised when no configuration data for connections found
    """

class Config(object):
    """Reads config files for source directories and db connection info

    Attributes:
        connections: path for connections file
        sources: path for sources file
    """
    def __init__(self):
        self._sources = {}
        self._connections = []

    @property
    def sources(self):
        return self._sources

    @sources.setter
    def sources(self, source_cfg):
        log = getLogger('Rkive.Config')
        if self._sources:
            return self._sources
        try:
            log.debug("Reading {0} source file".format(source_cfg))
            with open(source_cfg) as s:
                d = yaml_load(s)
                if d is None:
                    raise NoSourcesError
                if not isinstance(d,dict):
                    raise NoSourcesError
                for source_folder, source_category in d.items():
                    source_category = source_category.lower()
                    if not source_folder in self._sources:
                        self._sources[source_category] = []
                    self._sources[source_category].append(source_folder)
        except EnvironmentError as e:
            log.fatal("Environment error {0} encountered".format(str(e)))
            self._sources={} 
            return
        except NoSourcesError:
            log.warn("No sources in file {0}".format(source_cfg))
            self._sources={} 

    @property
    def connections(self):
        return self._connections

    @connections.setter
    def connections(self, connections_cfg):
        log = getLogger('Rkive.Config')
        log.info("hellp")
        print("XXXXXXXXXXX")
        if self._connections:
            return 
        try:
            log.debug("Reading {0} connections file".format(connections_cfg))
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
                    if not 'label' in conn:
                        raise NoConnectionsError
                    dbtype = conn['type']
                    path = conn['path']
                    label = conn['label']
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
                    self._connections.append({'status':status, 'label': label, 'url':url})
        except EnvironmentError as e:
            log.warn("Environment Error "+str(e))
            self._connections={}
            return
        except NoConnectionsError:
            log.warn("No connections")
            self._connections={}
            return 

    @property
    def music(self):
        if not "music" in self._sources:
            return None
        return self._sources["music"]
    
    @property
    def movies(self):
        if not "movies" in self._sources:
            return None
        return self._sources["movies"]

    @property
    def local_live_connections(self):
        return([c[2] for c in self._connections if 'live' in c[0] and 'local' in c[1]])

    @property 
    def remote_live_connections(self):
        return ([c[2] for c in self._connections if 'live' in c[0] and 'remote' in c[1]])
