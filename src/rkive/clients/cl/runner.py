class RkiveRunner:
    def run(script, log, install_path, media_server):
        if script == 'rk_tag':
            from rkive.clients.cl.tagger import Tagger
            Tagger(logfolder=log).run()
        if script == 'rk_local_index_gui':
            from rkive.clients.cl.index import IndexClient
            uri = 'sqlite:///{0}data/index.db'.format(install_path)
            engine = create_engine(uri)
            index_client = IndexClient(logfolder=log, engine=engine)
            if index_client.display == 'kivy':
                from kivy.base import runTouchApp
                from rkive.clients.kivy.index import MasterDetailView
                master_detail = MasterDetailView(index_client, width=800)
                runTouchApp(master_detail)
                return
        if script == 'rk_report':
            from rkive.clients.cl.reporter import ReportClient
            ReportClient(logfolder=log).run()
        if script == 'markup':
            from rkive.clients.cl.markup import MarkupClient
            MarkupClient(logfolder=log).run()
        if script == 'rk_convert':
            from rkive.clients.cl.converter import ConvertClient
            ConvertClient(logfolder=log).run()
        if script == 'rk_make_local_index':
            from rkive.clients.cl.makeindex import MakeIndexClient
            from rkive.clients.config import Config
            c = Config(install_path)
            urls = c.get_local_connections()
            sources = c.get_sources()
            MakeIndexClient(logfolder=log, urls=urls, sources=sources).run()
        if script == 'rk_make_index':
            from rkive.clients.cl.makeindex import MakeIndexClient
            from rkive.clients.config import Config
            c = Config(install_path)
            urls = c.get_remote_connections()
            sources = c.get_sources()
            MakeIndexClient(logfolder=log, urls=urls, sources=sources).run()
