import os
from logging import getLogger


#
# we never process folders, only files
def scantree(path, recursive=False):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            if recursive:
                yield from scantree(entry.path, recursive)
        else:
            yield entry


def visit_files(
        folder='.',
        funcs=[],
        exclude=None,
        include=None,
        recursive=False):
    log = getLogger('Rkive.Files')
    for file in scantree(folder, recursive):
        root, name = os.path.split(file.path)
        log.debug("Processing file: {0}".format(file.path))
        if (callable(exclude) and exclude(root, name)):
            continue
        if callable(include) and include(file.path):
            log.debug("Processing file: {0}".format(file.path))
            for func in funcs:
                func(file.path)
