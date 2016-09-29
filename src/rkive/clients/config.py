from yaml import load
import os.path
import logging

class Config:

    def __init__(self, home):
        self.sources = {}
        self.connections = []
        self.home = home

    def read(self):
        #read the sources
        source = os.path.join(self.home, 'sources.yml')
        with open(source) as s:
            d = load(s)
            for k, v in d.items():
                reverse_key = v.lowercase()
                if not reverse_key in self.sources:
                    self.sources[reverse_key] = []
                self.sources[reverse_key].append(k)
        conns_cfg = os.path.join(self.home, 'connections','default.yml')

    def get_music(self):
        if not "music" in self.sources:
            return None

    def get_movies(self):
        if not "movies" in self.sources:
            return None
        return self.sources["movies"]

    def get_live_connections(self):
        connections = []
        return connections
