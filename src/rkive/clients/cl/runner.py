class RkiveRunner:
    def run(script, logs, install_path, media_server):
        if script == 'rk_tag':
            from rkive.clients.cl.tagger import Tagger
            Tagger(logfolder=log).run()
        if script == 'rk_index_gui':
            from rkive.clients.index import IndexClient
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
            uri = 'sqlite:///{0}data/index.db'.format(install_path)
            engine = create_engine(uri)
            MakeIndexClient(logfolder=log, engine=engine).run()
        if script == 'rk_make_index':
            from rkive.clients.cl.makeindex import MakeIndexClient
            uri ='postgresql://postgres:postgres@{0}/mediaindex'.format(media_server)
            engine = create_engine(uri)
            MakeIndexClient(logfolder=log, engine=engine).run()

