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
          'rkive' : 'rkive',
          'rkive.clients' : 'rkive/clients',
          'rkive.uploader' : 'rkive/uploader',
          'rkive.index' : 'rkive/index',
          'rkive.clients.cl': 'rkive/clients/cl',
          'rkive.clients.web' : 'rkive/clients/web',
          'rkive.clients.gui' : 'rkive/clients/gui'
      }
)
