import argparse
import os.path

class FolderValidation(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(FolderValidation, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        p = os.path.expanduser(values)
        values = p
        if not os.path.isdir(values): 
            raise Exception("No valid base folder")
        setattr(namespace, self.dest, values)

class FileValidation(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(FileValidation, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        p = os.path.expanduser(values)
        values = p
        if not os.path.exists(values): 
            raise Exception("File {0} does not exist".format(values))
        setattr(namespace, self.dest, values)

class GetOpts(object):
    
    def __init__(self, parent=None):
        self.p = argparse.ArgumentParser()
        self.parent=parent
    
    def get_opts(self):
        self.p.add_argument('--base',  nargs=1, default='.', help="Base at which to start searching for files", action=FolderValidation)
        self.p.add_argument('--debug',  default=False, help="More output", action='store_true')
        self.p.add_argument('--dryrun', default=False, help="Print out actions that would have been performed", action='store_true')
        self.p.add_argument('--quiet', default=False, help="Do not print logs to stdout", action='store_true')
        self.p.add_argument('--console', default=False, help="log to console", action='store_true')
        self.p.parse_args(namespace=self.parent)
