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
                if not isinstance(d, dict):
                    raise NoSourcesError
                for source_folder, source_category in d.items():
                    source_category = source_category.lower()
                    if source_folder not in self._sources:
                        self._sources[source_category] = []
                    self._sources[source_category].append(source_folder)
        except EnvironmentError as e:
            log.fatal("Environment error {0} encountered".format(str(e)))
            self._sources = {}
            return
        except NoSourcesError:
            log.warn("No sources in file {0}".format(source_cfg))
            self._sources = {}

    @property
    def connections(self):
        return self._connections

    @connections.setter
    def connections(self, connections_cfg):
        log = getLogger('Rkive.Config')
        if self._connections:
            return
        try:
            log.debug("Reading {0} connections file".format(connections_cfg))
            with open(connections_cfg) as cf:
                conns = yaml_load(cf)
                if conns is None:
                    raise NoConnectionsError
                if not isinstance(conns, list):
                    raise NoConnectionsError
                for conn in conns:
                    # Test for must have parameters first
                    if 'type' not in conn:
                        raise NoConnectionsError
                    if 'path' not in conn:
                        raise NoConnectionsError
                    if 'status' not in conn:
                        raise NoConnectionsError
                    if 'location' not in conn:
                        raise NoConnectionsError
                    dbtype = conn['type']
                    path = conn['path']
                    location = conn['location']
                    status = conn['status']
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
                    url = f'{dbtype}://{username}{password}{host}{port}/{path}'
                    if not os.path.isfile(path):
                        fh = open(path, 'w')
                        fh.close()
                    c = {
                        'status': status,
                        'url': url,
                        'location': location
                    }
                    self._connections.append(c)
        except EnvironmentError as e:
            log.warn("Environment Error "+str(e))
            self._connections = {}
            return
        except NoConnectionsError:
            log.warn("No connections")
            self._connections = {}
            return

    @property
    def music(self):
        if "music" not in self._sources:
            return None
        return self._sources["music"]

    @property
    def movies(self):
        if "movies" not in self._sources:
            return None
        return self._sources["movies"]

    def local_live_connections(self):
        conns = []
        for c in self._connections:
            if c['status'] == 'live' and c['location'] == 'local':
                conns.append(c)
        return conns

    def remote_live_connections(self):
        conns = []
        for c in self._connections:
            if c['status'] == 'live' and c['location'] == 'remote':
                conns.append(c)
        return conns
