#!/usr/bin/env python
from rkive.clients.files import visit_files
from rkive.index.movie import movie
import os.path
import re

movies={}


film_re = re.compile('(.*?) \((.*?), (\d\d\d\d)\)')

def index_movies(root, name):
    fp = '/'.join([root, name])
    path, leaf=os.path.split(fp)
    dp, ld = os.path.split(path)
    if ld in movies:
        return
    m = film_re.match(ld)
    if m:
        movie = m.group(1)
        director = m.group(2)
        year = m.group(3)
        movies[ld] = Movie(movie, director, year)

root='/media/azure/Multimedia/Movies/'
visit_files(folder=root, funcs=[index_movies],recursive=True)
for m in movies.values():
    m.p()
