#!/usr/bin/env python
import os.path
import os
import argparse

def visit_files(base):
    local_base = '/Users/roger/Music/Rips'
    for root, dirs, files in os.walk(base):
        for d in dirs:
            if (d == '.AppleDouble'):
                dirs.remove(d)
        for f in files:
            if (f == '.DS_Store'):
                continue
            fp = os.path.join(root, f)

            if fp.endswith('.cue'):
                (p, b) = os.path.split(fp)
                (n, ext) = b.rsplit('.', 1)
                flac = os.path.join(p, n+'.flac')
                ape = os.path.join(p, n+'.ape')
                if os.path.exists(flac) or os.path.exists(ape):
                    remote_path = '/'.join(fp.split('/')[:-1])
                    relative_path = fp.split('/')[4:-1]
                    lp = '/'.join([local_base]+relative_path)
                    l = "\t".join([lp, remote_path])
                    print(l)
if (__name__ == '__main__'):
    p = argparse.ArgumentParser()
    p.add_argument('--root', nargs=1, required=True)    
    args = p.parse_args()
    root = args.root[0]
    visit_files(root)
