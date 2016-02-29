import os
from enum import Enum
import rkive.clients.log
from rkive.clients.cl.opts import GetOpts, FolderValidation
from rkive.clients.files import visit_files
from logging import getLogger

class Status(Enum):
    todo = 1
    done = 2

class Job(object):

    def __init__(self, relative_path='', base='', target='' ):
        self.relative_path = relative_path
        self.base = base
        self.target = target
   
    def action(self):
        pass

class Copy(Job):

    def action(self):
        self.copy()

    def copy(self):
        pass

class Remove(Job):

    def action(self):
        self.remove()

    def remove(self):
        pass

class BackupClient(object):

    def run(self, logloc=""):
        try:
            go = GetOpts(parent=self)
            go.p.add_argument(
                '--target',
                nargs=1,
                help="base folder of backup sector",
                action=FolderValidation,
                required=True)
            go.get_opts()
            rkive.clients.log.LogInit().set_logging(
                location=logloc, 
                filename='backup.log', 
                debug=self.debug, 
                console=self.console)
            self.work = []
            self.build_jobs(self.base, self.target)
            self.run_jobs()
        except SystemExit:
            pass
    
    def run_jobs(self):
        for job in self.work:
            job.action()

    def build_jobs(self, base, target):
        self.tier1_base = self.get_folders(base)
        self.tier1_tgt = self.get_folders(target)
        #first check to see if we have to copy stuff to the target
        for v in self.tier1_base:
            if not v in self.tier1_target:
                job = Copy(
                    relative_path = v,
                    base = base,
                    target = target)
                self.work.append(job)
        # check to see if we have to remove stuff from the target
        for v in self.tier1_target:
            if not v in self.tier1_target:
                job = Remove(
                        relative_path = v,
                        target = base
                        )
                self.work.append(job)
        # look for the files to copy
        self.tier2_base = {}
        self.tier2_tgt = {}
        visit_files(target, funcs=[add_file_to_tier2_base])
        visit_files(target, funcs=[add_file_to_tier2_tgt])
        for n,v in self.tier2_base.items():
            if not n in self.tier2_target:
                relative_path = '/'.join([n,v])
                job = Copy(
                    relative_path = relative_path,
                    base = base,
                    target = target)
                self.work.append(job)
            else:
                fp_base = os.path.join(base, n, v)
                fp_tgt - os.path.join(target, n, v)
                modt_base = os.stat(fp_base)[8]
                modt_tgt = os.stat(fp_tgt)[8]
                if modt_base > modt_tgt:
                    relative_path = '/'.join([n,v])
                    job = Copy(
                        relative_path=relative_path,
                        target=target
                        )
                    self.work.append(job)
        # now do the delete 
        for n,v in self.tier2_tgt.items():
            if not n in self.tier2_base:
                job = Remove(
                    relative_path=v)
                self.work.append(job)

    def add_file_to_tier2_base(self, root, filename):
        self.tier2_base[root] = filename

    def add_file_to_tier2_base(self, root, filename):
        self.tier2_tgt[root] = filename

    def get_folders(self, root, folder):
        folders = {}
        for root, dirs, files in os.walk(target, topdown=False):
            for d in dirs:
                folders[d] = os.path.join(root, d)
        return folders

