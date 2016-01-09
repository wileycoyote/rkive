import argparse
import os.path

class BaseAction(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(BaseAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        p = os.path.expanduser(values)
        values = p
        if not os.path.isdir(values): 
            raise Exception("No valid base folder")
        setattr(namespace, self.dest, values)

class GetOpts(object):
    
    def __init__(self, parent=None):
        self.p = argparse.ArgumentParser()
        self.parent=parent
    
    def get_opts(self):
        self.p.add_argument('--debug',  help="More output", action='store_true')
        self.p.add_argument('--dryrun', help="Print out actions that would have been performed", action='store_true')
        self.p.add_argument('--quiet', help="Do not print logs to stdout", action='store_true')
        self.p.add_argument('--console', help="log to console", action='store_true')
        self.p.parse_args(namespace=self.parent)
