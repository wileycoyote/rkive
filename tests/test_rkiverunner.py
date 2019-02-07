import unittest
from rkive.clients.cl.runner import RkiveRunner


class TestTagger(unittest.TestCase):

    base = "/Users/roger/Upload"

    def test_make_local_index(self):
        r = RkiveRunner('rk_index', 'local_index', '', '')
        r.run()
