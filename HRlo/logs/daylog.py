#!/usr/bin/env python3
import re
import datetime

from . import dayutils


def pairwise(l):
   iterator = iter(l)
   a = next(iterator)
   for b in iterator:
      yield a, b
      a = next(iterator)
   yield a, b


class DayLog(dict):
   """Class to management of login/logout accesses.
   """

   def __init__ (self, date = None, logs = None):
      """__init__(date, logs)
      """

      # date of day
      self['date'] = date
      # list of logs
      self['logs'] = []
      # total uptime
      self['uptime'] = datetime.timedelta(0)

      if not logs:
         return

      # check if logs are odds
      pass

      self['logs'] = [ datetime.datetime.combine( self['date'], dayutils.str2time(i) ) for i in logs ]

      for i in [ o-i for i, o in pairwise(self['logs']) ]:
         self['uptime'] += i


   def __str__(self):
      s = ''
      if not self['date'] or not self['logs']:
          return s
      s += "[LOGS] "
      s +=          "{:.<20}{}\n".format( 'Date', str(self['date'].date()) )
      s += " "*7 +  "{:.<20}{}\n".format( 'Uptime', dayutils.sec2str(self['uptime'].total_seconds()) )
      s += " "*7 +  "{:.<20}[ {} ]".format( 'Logs', ", ".join([ i.time().strftime(dayutils.fmt_time) for i in self['logs']]) )
      return s

   def __add__(self, other):
      l1 = [i.time().strftime(dayutils.fmt_time) for i in self['logs']]
      l2 = [i.time().strftime(dayutils.fmt_time) for i in other['logs']]
      return DayLog( date = datetime.datetime(1970, 1, 1), logs = l1 + l2 )

   def __radd__(self, other):
      return self.__add__(other)

   def id (self):
      """Return date in format YYYYMMDD"""
      return self['date'].strftime(dayutils.fmt_id)

   def date (self, fmt=False):
      """Return date.
         If format=True return date in format DD/MM/YYYY."""
      if fmt:
         return self['date'].strftime(dayutils.fmt_day)
      else:
         return self['date']

   def day (self):
      """Return date (datetime class)"""
      return self['date']

   def uptime(self):
      """Return uptime in seconds"""
      return self['uptime']

   def uptimes(self, fmt = None):
       ups = [ o-i for i, o in pairwise(self['logs']) ]
       if fmt:
           return [ dayutils.sec2str(u.total_seconds())  for u in ups ]
       else:
           return ups

   def login (self):
      """Return earlier login"""
      return self['logs'][0]

   def logout (self):
      """Return latest login"""
      return self['logs'][-1]

   def logins (self):
      """Return list of all logins"""
      return [i for i, o in pairwise(self['logs']) ]

   def logouts (self):
      """Return list of all logouts"""
      return [o for i, o in pairwise(self['logs']) ]

   def logs (self, fmt = None):
      """Return list of logs"""
      if fmt:
         return [ i.strftime(fmt) for i in self['logs']]
      else:
         return self['logs']

