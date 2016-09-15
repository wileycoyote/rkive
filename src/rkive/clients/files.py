import os
from logging import getLogger

def scantree(path, recursive=False):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        if recursive and entry.is_dir(follow_symlinks=False):
            scantree(entry.path)
        else:
            yield entry

def visit_files(folder='.', funcs=[], exclude=None, include=None, recursive=False):
    log = getLogger('Rkive.Files')
    for file in scantree(folder, recursive):
        root, name = os.path.split(file)
        if (exclude and exclude(root, name)):
            continue
        if include and include(root, name):
            for func in funcs:
                func(root, name)
        else:
            func(root, name)
