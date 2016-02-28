import os
import rkive.clients.log
import rkive.clients.cl.opts
from rkive.clients.files import visit_files

class Job(object):
    action=Action.leave
    object_type = Object.type
    time_last_mod = ''
    relative_path = ''
    full_path = ''
    status = ''

class BackupClient(object):

    def run(self, logloc=""):
        try:
            go = rkive.clients.cl.opts.GetOpts(parent=self)
            go.p.add_argument(
                '--target',
                nargs=1,
                help="name of cue file to be split",
                action=DirValidation,
                required=True)
            go.get_opts()
            rkive.clients.log.LogInit().set_logging(
                location=logloc, 
                filename='backup.log', 
                debug=self.debug, 
                console=self.console)
            self.cmp_tier1(self.base, self.target)
        except SystemExit:
            pass
    
    def cmp_tier1_folders(self, base, target):
        self.tier1_base = self.get_folders(base)
        self.tier1_tgt = self.get_folders(target)
        self.tier1_work = {}

    def get_folders(self, target):
        folders = {}
        for root, dirs, files in os.walk(target, topdown=False):
            for d in dirs:
                folders[d] = os.path.join(root, d)
        return folders
    def get_tier2_folders(self):
        pass
