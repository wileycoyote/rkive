import os

class Files(object):
    def visit(self, base='.', funcs=[], exclude=None, include=None):
        for root, dirs, files in os.walk(base, topdown=False):
            for name in files:
                if (exclude and exclude(root, name)):
                    continue
                for func in funcs:
                    if include:
                        if include(root, name):
                            func(root, name)
                        continue
                    func(root, name)
            for name in dirs:
                base = os.path.join(root, name)
                self.visit(
                    base=base, 
                    funcs=funcs, 
                    exclude=exclude, 
                    include=include)
