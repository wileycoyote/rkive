import os

class Distributer(object):

    base = os.path.join(os.environ['HOME'],"Uploads", "data") 

    def put(self):
        pass

    def get(self):
        pass

    def config(self):
        pass

    def logging(self):
        pass

    def visit(self, base='.', funcs=[], excs=[]):
        for root, folders, files in os.walk(base):
            for folder in folders:
                root_path = '/'.join([base,folder])
                self.visit(base=root_path, func=func, exc=exc)
            for f in files:
                for exc in excs:
                    if exc == f:
                        break
                else:
                    root_path
                    fp = '/'.join([root_path, f])
                    for func in funcs:
                        func(fp)

    def run(self):
        self.visit(base=self.base, funcs=[self.put],excs=['.DS_Store'])

