import os.path
import os
from logging import getLogger

class Manager(Distributer):

    def visit(base='.', func=[], exc=[]):
        log = getLogger('Rkive')
        for root, dirs, files in os.walk(base):
            for f in files:
                if (f in exc):
                    continue
                fp = os.path.join(root, f)
                for f in func:
                    f(fp)

    def distribute_files(self):
        log = getLogger('Rkive.Uploader')
        if (self.dryrun):
            log.warn("Running script in dryrun mode without action; will report only")
        if (self.check_for_sanitization_flag()):
            log.info("Uploading files with sanitized filenames")
        else:
            log.warn("Uploading files with un-sanitized filenames")
        self.set_list_of_folders()
        self.visit(base=self.base, func=[self.put], exc=['.DS_Store'])

    def check_for_sanitisation_flag(self):
        pass

    def put(self):
        pass

    def config(self):
        pass
