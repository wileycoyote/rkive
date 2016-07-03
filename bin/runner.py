#!/usr/bin/env python
import os.path
import sys
script =  os.path.basename(sys.argv[0])
log = os.path.join(os.path.expanduser('~'), 'logs')
if (script == 'rk_tag'):
    from rkive.clients.cl.tagger import Tagger
    Tagger().run(logloc=log)
if (script == 'rk_index'):
    from rkive.clients.cl.index import IndexClient
    IndexClient().run(logloc=log)
if (script == 'rk_report'):
    from rkive.clients.cl.reporter import ReportClient
    ReportClient().run(logloc=log)
if (script == 'markup'):
    from rkive.clients.cl.markup import MarkupClient
    MarkupClient().run(logloc=log)
if (script == 'rk_convert'):
    from rkive.clients.cl.converter import ConvertClient
    ConvertClient().run(logloc=log)
if (script == 'rk_make_index'):
    from rkive.clients.cl.makeindex import MakeIndexClient
    MakeIndexClient().run(logloc=log)
