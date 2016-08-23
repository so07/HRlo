#!/usr/bin/env python3
from distutils.core import setup

try:
   from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
   from distutils.command.build_py import build_py

from HRlo import config

setup(

   name=config.name,
   version=config.version,
   description=config.description,
   long_description=config.long_description,
   author=config.author,
   author_email=config.author_email,
   maintainer=config.maintainer,
   url=config.url,
   download_url=config.url,
   requires=['requests'],
   packages=['HRlo', 'HRlo/logs', 'HRlo/logs/dayutils'],
   scripts=['bin/accaerralo', 'bin/HRlo',
            'bin/HRday', 'bin/HRget',
            'bin/HRpresence', 'bin/HRcompany',
            'bin/HRtotalizator',
            'bin/HRutils'],
   cmdclass={'build_py': build_py},

   classifiers=[
       'Development Status :: 3 - Alpha',
       'Programming Language :: Python :: 3',
       'Programming Language :: Python :: 3.2',
       'Programming Language :: Python :: 3.3',
       'Programming Language :: Python :: 3.4',
   ],

)
