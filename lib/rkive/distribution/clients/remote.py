from rkive.distribution.net.clients import UploadClient
from rkive.distribution.config import ConfigManager
from rkive.distribution.clients.distributer import Distributer

class RemoteDistributer(Distributer):

    def __init__(self):
        self.server_connections = {}
        self.server_cache = {}
        self.folders = {}

    def put(self, src):
      	f = src.split('/')
        b = self.base.split('/')
        rp  = '/'.join(f[len(b):])
        db_pk = self.get_path_key(rp)
        server = self.get_server(db_pk)
        if (self.dryrun):
            log.info("Dryrun: Would upload {0} to {1} on {2}".format(src, tgt, server.ipaddress))
	    return
       	conn = self.connect_to_server(server)

        log = logging.getLogger('Rkive.Uploader')
        try:
            log.info("upload {0} to {1}".format(src, tgt))
            # build the folders first
            (tree, base) = os.path.split(tgt)
            conn.mkdir(tree)
            tries = 0
            while(1):
                if (self.rerun):
                    rows = uploader.log.DBSession.query(Log).filter(Log.remote==tgt, Log.ipaddress==self.ipaddress)
                    if (rows):
                        log.info("remote file {0} found in database; skipping".format(tgt))
                        return 
                try:
                    self.conn.put(src, tgt)
                    s = os.path.getsize(src)
                    l = uploader.log.Log(src, tgt, self.server, self.ipaddress, s)
                    uploader.log.DBSession.add(l)
                    return
                except Exception as e:
                    log.warn("Failure: "+e)
                    if (tries == 3):
                        log.fatal("Giving up loading {0} to {1} on {0}".format(src, tgt, self.server))
                        return
                    time.sleep(30)
                    tries = tries + 1
        except Exception as e:
            log.warn(e.message)

    def get_server(self, db_pk):
        log = getLogger('Rkive.Uploader')
        if (db_pk is None):
            raise("No database key has been passed, will not process")
        if (db_pk in self.server_cache):
            return self.server_cache[db_pk]
        if (db_pk not in self.folders):
            raise("Folder {0} on disk not in database; will not be uploaded".format(db_pk))
        # work out which one the file is going to 
        chosen_server = None
        n = 0
        for server in self.folders[db_pk]:
            conn  = self.connect_to_server(server)
            s = conn.get_partition_size(server.partition)
            if (s > n):
                n = s
                chosen_server = server
        if (chosen_server is None):
            raise("No server found for {0}".format(db_pk))
        log.info("chosen server is: {0}".format(chosen_server.server_name))
        # record where it went
        self.server_cache[db_pk] = chosen_server
        return chosen_server

    def connect_to_server(self, s):
        log = getLogger('Rkive.Uploader')
        server_key = s.ipaddress
        if (self.server_connections.has_key(server_key)):
            return self.server_connections[server_key]
        log.info("address: {0}".format(s))
        conn = UploadClient(s.ipaddress, s.port, s.username)
        self.server_connections[s.ipaddress] = conn
        return conn

     def set_list_of_folders(self):
        log = getLogger('Rkive.ServerFacade')
        from uploader.config import db, LocalFolder, Server
        rows = db.query(LocalFolder.remote_folder, Server.username, Server.ipaddress, LocalFolder.server_name, LocalFolder.local_folder, Server.partition).join(Server).all()
        folders = {}
        for row in rows: 
            if not row.local_folder in folders:
                folders[row.local_folder] = []
            folders[row.local_folder].append(row)
        self.folders = folders
        return folders
