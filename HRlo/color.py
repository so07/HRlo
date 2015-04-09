#!/usr/bin/env python3
import sys

NORMAL = "\033[0m"

BLACK = "\033[0;30m"
BLUE = "\033[0;34m"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
RED = "\033[0;31m"
PURPLE = "\033[0;35m"
BROWN = "\033[0;33m"
GRAY = "\033[0;37m"
BOLDGRAY = "\033[1;30m"
BOLDBLUE = "\033[1;34m"
BOLDGREEN = "\033[1;32m"
BOLDCYAN = "\033[1;36m"
BOLDRED = "\033[1;31m"
BOLDPURPLE = "\033[1;35m"
BOLDYELLOW = "\033[1;33m"
WHITE = "\033[1;37m"

class color:

   def __init__(self, c):
      self.color = c

   def __call__(self, f):
      def wrapped(*args, **kw):
         if (sys.stdout.isatty()):
            return self.color + f(*args, **kw) + NORMAL
         else:
           return f(*args, **kw)
      return wrapped


if __name__ == '__main__':

   s1 = 'decorating str works only once (in RED!)'

   col = color(BOLDRED)( str )

   print( col(s1) )

