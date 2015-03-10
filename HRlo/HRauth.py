#!/usr/bin/env python3
import re
import os
import sys

import getpass
try:
   from configparser import SafeConfigParser
except:
   from ConfigParser import SafeConfigParser

class HRauth(dict):

   HRauth_config_option = 'HRauth'

   def __init__(self, **kwargs):

      dict.__init__(self, **kwargs)

      self['required'] = ['host', 'username', 'idemploy']

      # read from config_file
      self._read_config_file(kwargs['config_file'])
      # read from args
      self.update( {k: kwargs[k] for k in self['required'] if kwargs.get(k, None)} )

      if self['save']:
         self._write_config_file(self['config_file'])

      self['password'] = getpass.getpass()

      self._check_required()

   def _check_required(self):
      missing = []
      for k in self['required']:
         if not self.get(k, False):
            missing.append(k)

      if not missing:
         return
      else:
         print("[HRauth] *** ERROR *** missing required args :", ", ".join(missing))
         sys.exit(1)


   def _read_config_file(self, fname):

      if not os.path.isfile(fname):
         return

      parser = SafeConfigParser()
      parser.read(fname)

      self.update( {k: parser.get(self.HRauth_config_option, k) for k in parser.options(self.HRauth_config_option)} )


   def _write_config_file(self, fname):
       parser = SafeConfigParser()

       parser.add_section(self.HRauth_config_option)

       if self.get('host', None):
          parser.set(self.HRauth_config_option, 'host', self['host'])
       if self.get('username', None):
          parser.set(self.HRauth_config_option, 'username', self['username'])
       if self.get('idemploy', None):
          parser.set(self.HRauth_config_option, 'idemploy', str(self['idemploy']))

       with open(fname, "w") as f:
          parser.write(f)


   def host(self):
      return self['host']
   def username(self):
      return self['username']
   def idemploy(self):
      return self['idemploy']
   def password(self):
      return self['password']


def add_parser(parser):

   authparser = parser.add_argument_group('HR authentication options')

   authparser.add_argument('-u', '--username',
                           help='Username')

   authparser.add_argument('-i', '--idemploy',
                           help='ID employee')

   authparser.add_argument('-a', '--url',
                           dest='host',
                           help='HR url')

   authparser.add_argument('-c', '--config-file',
                           default = os.path.join( os.path.expanduser("~"), '.HRlo'),
                           help='Configuration file')

   authparser.add_argument('-s', '--save',
                           action='store_true',
                           help='Save HR authentication options in HRauth config file')

   args = parser.parse_args()
   return vars(args)


def main ():

   import HRget
   import argparse

   parser = argparse.ArgumentParser(prog='',
                                    description='descriptions',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   add_parser(parser)

   args = parser.parse_args()

   #print(args)

   auth = HRauth(**vars(args))

   hrget = HRget.HRget(auth)

   if hrget:
      print("Successfully login!")


if __name__ == '__main__':
    main()
