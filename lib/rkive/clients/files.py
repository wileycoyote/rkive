import os

class Files(object):
    def visit(self, base='.', funcs=[], exclude=[]):
        for root, dirs, files in os.walk(base, topdown=False):
            for name in files:
                print(os.path.join(root, name))
                fp = os.path.join(root, name)
                for func in funcs:
                    func(fp)
            for name in dirs:
                print(os.path.join(root, name))
                base = os.path.join(root, name)
                self.visit(base, funcs=funcs)
