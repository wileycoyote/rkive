import unittest
from rkive.clients.cl.opts import GetOpts
import sys

class Dummy(object):
    pass

class TestGetOpts(unittest.TestCase):
    
    def test_debug(self):
        d = Dummy()
        g = GetOpts(d)
        sys.argv = ["prog", "--debug"]
        g.get_opts()
        self.assertTrue(d.debug)

    def test_dryrun(self):
        d = Dummy()
        g = GetOpts(d)
        sys.argv = ["prog", "--dryrun"]
        g.get_opts()
        self.assertTrue(d.dryrun)
    
    def test_quiet(self):
        d = Dummy()
        g = GetOpts(d)
        sys.argv = ["prog", "--quiet"]
        g.get_opts()
        self.assertTrue(d.quiet)

    def test_dryrun(self):
        d = Dummy()
        g = GetOpts(d)
        sys.argv = ["prog", "--console"]
        g.get_opts()
        self.assertTrue(d.console)
