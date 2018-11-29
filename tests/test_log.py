import unittest
from rkive.clients.log import LogInit
import sys
import logging

class TestLogInit(unittest.TestCase):


    def test_log_info(self):
        l = LogInit()
        l.level = logging.INFO
        l.logger = 'logs/test.log'
        with self.assertLogs('Rkive', level='INFO') as cm:
            logging.getLogger('Rkive').info('first message')
            logging.getLogger('Rkive.bar').error('second message')
            self.assertEqual(cm.output, ['INFO:Rkive:first message',
                                 'ERROR:Rkive.bar:second message'])

    def test_log_debug(self):
        l = LogInit()
        l.level= logging.DEBUG
        l.logger = 'logs/test.log'
        with self.assertLogs('Rkive', level='DEBUG') as cm:
            logging.getLogger('Rkive').debug('first message')
            logging.getLogger('Rkive.bar').error('second message')
            self.assertEqual(cm.output, ['DEBUG:Rkive:first message',
                                 'ERROR:Rkive.bar:second message'])
