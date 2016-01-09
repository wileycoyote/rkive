#!/usr/bin/env python
import os.path
import sys

actual_folder, script = os.path.split(sys.argv[0])
root_folder, leaf = os.path.split(os.path.realpath(__file__))
root_folder,leaf = os.path.split(root_folder)
log = os.path.join(root_folder, 'logs')
lib = os.path.join(root_folder, 'lib')
sys.path.append(lib)

if (script == 'rk_tag'):
    from rkive.clients.cl.tagger import Tagger
    Tagger().run(log=log)
if (script == 'rk_upload'):
    from rkive.clients.cl.uploader import Uploader
    Uploader().run(log=log)
if (script == 'rk_index'):
    from rkive.clients.cl.indexer import Indexer
    Indexer().run(log=log)
if (script == 'rk_report'):
    from rkive.clients.cl.reporter import ReportClient
    ReportClient().run(log=log)
