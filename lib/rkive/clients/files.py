import os
from logging import getLogger

def visit_files(folder='.', funcs=[], exclude=None, include=None):
    log = getLogger('Rkive.Files')
    for root, dirs, files in os.walk(folder, topdown=False):
        for name in files:
            log.debug(name)
            if (exclude and exclude(root, name)):
                continue
            for func in funcs:
                if include:
                    if include(root, name):
                        func(root, name)
                    continue
                func(root, name)
        for name in dirs:
            base = os.path.join(root, name)
            visit_files(
                folder=base, 
                funcs=funcs, 
                exclude=exclude, 
                include=include)
