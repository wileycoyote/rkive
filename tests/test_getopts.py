import unittest
import tempfile
from rkive.clients.cl.opts import GetOpts as GetOpts
from rkive.clients.cl.opts import FileValidation
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
        """ Test that an existing base is detected
        """
        d = Dummy()
        tempdir=tempfile.gettempdir()
        sys.argv = ["prog", "--base",tempdir]
        p = GetOpts().get_parser()
        p.parse_args(namespace=d)
        self.assertTrue(d.console)

    def test_no_base(self):
        """ Base file non-existent
        """
        d = Dummy()
        tempdir='/xxx'
        sys.argv = ["prog", "--base",tempdir]
        p = GetOpts().get_parser()
        with self.assertRaises(Exception):
            p.parse_args(namespace=d)

    def test_file_validation(self):
        d = Dummy()
        tmpfile=tempfile.gettempdir()+'/rkive_tmpfile'
        f = open(tmpfile, 'w')
        f.close()
        sys.argv = ["prog", "--filename",tmpfile]
        p = GetOpts().get_parser()
        p.add_argument('--filename',  type=str, help="file to set attributes", action=FileValidation)
        p.parse_args(namespace=d)
        self.assertTrue(d.filename == tmpfile)

    def test_no_file_validation(self):
        d = Dummy()
        sys.argv = ["prog", "--filename",'/xxxxx']
        p = GetOpts().get_parser()
        p.add_argument('--filename',  type=str, help="file to set attributes", action=FileValidation)
        with self.assertRaises(Exception):
            p.parse_args(namespace=d)

    def test_recursive(self):
        d = Dummy()
        sys.argv = ["prog", "--recursive"]
        p = GetOpts().get_parser()
        p.parse_args(namespace=d)
        self.assertTrue(d.recursive)
