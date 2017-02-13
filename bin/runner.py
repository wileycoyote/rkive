#!/usr/bin/env python
import os.path
import sys
from rkive.clients.cl.runner import RkiveRunner
if __name__ == '__main__':
    script =  os.path.basename(sys.argv[0])
    base = os.path.dirname(sys.argv[0])
    install_path =os.path.dirname(base)
    logs = os.path.join(os.path.expanduser('~'), 'logs')
    media_server = '191.168.1.155'
    RkiveRunner(
        script=script, 
        logfolder=logs, 
        install_path=install_path, 
        media_server=media_server).run()
