#!/usr/bin/env python3
from distutils.core import setup

from HRlo import config

setup(

   name=config.name,
   version=config.version,
   description=config.description,
   author=config.author,
   author_email=config.author_email,
   url=config.url,
   packages=['HRlo', 'HRlo/logs'],
   scripts = ['bin/accaerralo', 'bin/HRlo', 'bin/HRday', 'bin/HRget'],

)
