#!/usr/bin/env python3
import re
import sys

import getpass

class HRauth(object):
   def __init__(self, host, username, idemploy, password):
      self._host     = host
      self._username = username
      self._idemploy = idemploy
      self._password = password

   def host(self):
      return self._host
   def username(self):
      return self._username
   def idemploy(self):
      return self._idemploy
   def password(self):
      return self._password


def add_parser(parser):

   parser = parser.add_argument_group('HR authentication options')

   parser.add_argument('-u', '--username',
                       required=True,
                       help='Username')

   parser.add_argument('-i', '--idemploy',
                       required=True,
                       help='ID employee')

   parser.add_argument('-a', '--url',
                       dest='host',
                       required=True,
                       help='HR url')


def main ():

   import argparse

   parser = argparse.ArgumentParser(prog='',
                                    description='descriptions',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   add_parser(parser)

   args = parser.parse_args()

   args.password = getpass.getpass()

   #print(args)

   dargs = vars(args)

   auth = HRauth(dargs['host'], dargs['username'], dargs['idemploy'], dargs['password'])

   import HRget

   hrget = HRget.HRget(auth)





if __name__ == '__main__':
    main()
