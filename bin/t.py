#!/usr/bin/env python
import os
filename = 'x'
path = os.path.dirname(os.path.realpath(__file__)) 
home = os.path.join(os.path.split(path)[0], filename)
print home
