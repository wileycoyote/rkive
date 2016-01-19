import os

class Files(object):
    def visit(self, base='.', funcs=[], exclude=None):
        for root, dirs, files in os.walk(base, topdown=False):
            for name in files:
                print(os.path.join(root, name))
                if (exclude and exclude(root, name)):
                    continue
                for func in funcs:
                    func(root, name)
            for name in dirs:
                print(os.path.join(root, name))
                base = os.path.join(root, name)
                self.visit(base, funcs=funcs, exclude=exclude)
