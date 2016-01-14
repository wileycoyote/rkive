#!/usr/bin/python3

import os
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--inc', help='number for incrementing track names',type=int,nargs=1,required=True)
args = parser.parse_args()
DEBUG = False
split_key = ' - '
increment = 2
files_by_track = {}
increment = args.inc[0]
print("increment value: {0}".format(increment))

for f in os.listdir():
    if (not f.endswith('.mp3')):
        continue
    [i,s] = f.split(split_key)
    j = int(i)
    files_by_track[j]  = f

reversed_index = list(reversed(list(files_by_track)))
for k in reversed_index:
    f = files_by_track[k]
    [i,s] = f.split(split_key)
    j = int(i)+increment
    k = format(j,"#02d")
    n = split_key.join([k,s])
    print("rename {0} to {1}".format(f,n))
    if (not DEBUG):
        os.rename(f,n)
