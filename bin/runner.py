#!/usr/bin/env python
import os.path
import sys
script =  os.path.basename(sys.argv[0])
log = os.path.join(os.path.expanduser('~'), 'logs')
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
if (script == 'markup'):
    from rkive.clients.cl.markup import MarkupClient
    MarkupClient().run(log=log)
