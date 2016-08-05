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
          'rkive.clients.kivy', 
          'rkive.clients.web', 
          'rkive.index',
          'kivy_ex'
      ],
      package_dir = {
          'rkive' : 'lib/rkive',
          'rkive.clients' : 'lib/rkive/clients',
          'rkive.uploader' : 'lib/rkive/uploader',
          'rkive.index' : 'lib/rkive/index',
          'kivy_ex' : 'lib/kivy_ex',
          'rkive.clients.cl': 'lib/rkive/clients/cl',
          'rkive.clients.web' : 'lib/rkive/clients/web',
          'rkive.clients.kivy' : 'lib/rkive/clients/kivy'
      }
)
