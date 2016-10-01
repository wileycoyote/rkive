import unittest
import tempfile
from rkive.clients.cl.opts import GetOpts
import sys

class Dummy(object):
    pass

class TestGetOpts(unittest.TestCase):
    
    def test_debug(self):
        d = Dummy()
        sys.argv = ["prog", "--debug"]
        p = GetOpts().get_parser()
        p.parse_args(namespace=d)
        self.assertTrue(d.debug)

    def test_dryrun(self):
        d = Dummy()
        sys.argv = ["prog", "--dryrun"]
        p = GetOpts().get_parser()
        p.parse_args(namespace=d)
        self.assertTrue(d.dryrun)
    
    def test_quiet(self):
        d = Dummy()
        sys.argv = ["prog", "--quiet"]
        p = GetOpts().get_parser()
        p.parse_args(namespace=d)
        self.assertTrue(d.quiet)

    def test_dryrun(self):
        d = Dummy()
        sys.argv = ["prog", "--console"]
        p = GetOpts().get_parser()
        p.parse_args(namespace=d)
        self.assertTrue(d.console)

    def test_base(self):
        d = Dummy()
        tempdir=tempfile.gettempdir()
        sys.argv = ["prog", "--base",tempdir]
        p = GetOpts().get_parser()
        p.parse_args(namespace=d)
        self.assertTrue(d.console)

    def test_recursive(self):
        self.fail("Must implement test_recursive")
