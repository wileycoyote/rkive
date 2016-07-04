#!/usr/bin/env python
import os.path
import sys
script =  os.path.basename(sys.argv[0])
log = os.path.join(os.path.expanduser('~'), 'logs')
if (script == 'rk_tag'):
    from rkive.clients.cl.tagger import Tagger
    Tagger(logfolder=log).run()
if (script == 'rk_index'):
    from rkive.clients.kivy.index import IndexClient
    IndexClient(logfolder=log).run()
if (script == 'rk_report'):
    from rkive.clients.cl.reporter import ReportClient
    ReportClient(logfolder=log).run()
if (script == 'markup'):
    from rkive.clients.cl.markup import MarkupClient
    MarkupClient(logfolder=log).run()
if (script == 'rk_convert'):
    from rkive.clients.cl.converter import ConvertClient
    ConvertClient(logfolder=log).run()
if (script == 'rk_make_index'):
    from rkive.clients.cl.makeindex import MakeIndexClient
    MakeIndexClient(logfolder=log).run()
