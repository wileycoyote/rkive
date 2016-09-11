import unittest
from rkive.clients.cl.runner import RkiveRunner

class TestTagger(unittest.TestCase):

    base = "/Users/roger/Upload"

    def test_make_local_index(self):
        RkiveRunner.run('rk_index','local_index','','')
