import os
from logging import getLogger

def visit_files(folder='.', funcs=[], exclude=None, include=None, recursive=False):
    log = getLogger('Rkive.Files')
    for root, dirs, files in os.walk(folder, topdown=True):
        for name in files:
            if (exclude and exclude(root, name)):
                continue
            for func in funcs:
                if include:
                    if include(root, name):
                        log.debug("apply funcs to {0}".format(name))
                        func(root, name)
                    continue
                func(root, name)
        if not recursive:
            log.debug("recursive set to false - do not follow folders down")
            del dirs[:]
        for name in dirs:
            base = os.path.join(root, name)
            log.debug("Visit folder {0}".format(base))
            visit_files(
                folder=base, 
                funcs=funcs, 
                exclude=exclude, 
                include=include,
                recursive=recursive)
