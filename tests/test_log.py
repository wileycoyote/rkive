import unittest
from rkive.clients.log import LogInit
import sys
import logging
from testfixtures import LogCapture

class TestLogInit(unittest.TestCase):


    def test_log_write_info(self):
        with LogCapture() as l:
            LogInit().config(False, False, 'logs/test.log')
            log = logging.getLogger('Rkive')
            log.info("HEllo")
            l.check(('Rkive', 'INFO', 'HEllo'),)

    def test_log_write_debug(self):
        with LogCapture() as l:
            LogInit().config(True, False, 'logs/test.log')
            log = logging.getLogger('Rkive')
            log.debug("Hello")
            l.check(('Rkive', 'DEBUG', 'Hello'),)
