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
   author=config.author,
   author_email=config.author_email,
   url=config.url,
   packages=['HRlo', 'HRlo/logs'],
   scripts = ['bin/accaerralo', 'bin/HRlo',
              'bin/HRday', 'bin/HRget',
              'bin/HRpresence', 'bin/HRcompany',
              'bin/HRtotalizator',
              'bin/HRutils'],
   cmdclass = {'build_py': build_py},

)
