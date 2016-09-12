#!/usr/bin/env python
from distutils.core import setup
setup(name='Rkive',
      version='1.0',
      description='Utilities for storing, labeling etc MP3, flac etc',
      author='Roger Day',
      author_email='c.roger.day@gmail.com',
      packages=[
          'rkive', 
          'rkive.clients',
          'rkive.clients.cl',
          'rkive.clients.gui', 
          'rkive.clients.web', 
          'rkive.index',
      ],
      package_dir = {
          'rkive' : 'src/rkive',
          'rkive.clients' : 'src/rkive/clients',
          'rkive.uploader' : 'src/rkive/uploader',
          'rkive.index' : 'src/rkive/index',
          'rkive.clients.cl': 'src/rkive/clients/cl',
          'rkive.clients.web' : 'src/rkive/clients/web',
          'rkive.clients.g' : 'src/rkive/clients/kivy'
      }
)
