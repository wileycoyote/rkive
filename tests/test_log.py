import unittest
from rkive.clients.log import LogInit
import sys
import logging

class TestLogInit(unittest.TestCase):

    base = "/Users/roger/Upload"

    def test_log_setup(self):
        LogInit().set_logging(location='logs', filename='test.log', debug=False, console=False)

    def test_log_write(self):
        LogInit().set_logging(location='logs', filename='test.log', debug=False, console=False)
        log = logging.getLogger('Rkive')
        log.info("HEllo")
        
