#!/usr/bin/env python3
import re
import datetime

#import dayutils

def pairwise(l):
   iterator = iter(l)
   a = next(iterator)
   for b in iterator:
      yield a, b
      a = next(iterator)
   yield a, b


class DayLog(object):
   """Class to management of login/logout accesses.
   """

   # oneLine, multiLine, multiLineVerbose
   strmode = 'multiLine'
   #strmode = 'oneLine'

   def __init__ (self, date = None, logs = None):
      """__init__(date, logs)
      """

      # date of day
      self._date = date
      # list of logs
      self._logs = []
      # total uptime
      self._uptime = datetime.timedelta(0)

      if not logs:
         return

      # check if logs are odds
      pass

      self._logs = [ datetime.datetime.combine( self._date, dayutils.str2time(i) ) for i in logs ]

      for i in [ o-i for i, o in pairwise(self._logs) ]:
         self._uptime += i


   def __str__(self):
      s = ''
      if not self._date or not self._logs:
          return s
      if DayLog.strmode == 'oneLine':
         s += '{} '.format( str(self._date.date()) )
         s += ' {} '.format( dayutils.sec2str(self._uptime.total_seconds()) )
         s += ' [ {} ]'.format( ", ".join([ i.time().strftime(dayutils.fmt_time) for i in self._logs]) )
      else:
         s += "[LOGS] "
         s +=          "{:.<20}{}\n".format( 'Date', str(self._date.date()) )
         s += " "*7 +  "{:.<20}{}\n".format( 'Uptime', dayutils.sec2str(self._uptime.total_seconds()) )
         s += " "*7 +  "{:.<20}[ {} ]".format( 'Logs', ", ".join([ i.time().strftime(dayutils.fmt_time) for i in self._logs]) )
      return s

   def __add__(self, other):
      l1 = [i.time().strftime(dayutils.fmt_time) for i in self._logs]
      l2 = [i.time().strftime(dayutils.fmt_time) for i in other._logs]
      return DayLog( date = datetime.datetime(1970, 1, 1), logs = l1 + l2 )

   def __radd__(self, other):
      return self.__add__(other)

   def id (self):
      """Return date in format YYYYMMDD"""
      return self._date.strftime(dayutils.fmt_id)

   def date (self):
      """Return date in format DD/MM/YYYY"""
      return self._date.strftime(dayutils.fmt_day)

   def day (self):
      """Return date (datetime class)"""
      return self._date

   def uptime(self):
      """Return uptime in seconds"""
      return self._uptime

   def uptimes(self, fmt = None):
       ups = [ o-i for i, o in pairwise(self._logs) ]
       if fmt:
           return [ dayutils.sec2str(u.total_seconds())  for u in ups ]
       else:
           return ups

   def login (self):
      """Return earlier login"""
      return self._logs[0]

   def logout (self):
      """Return latest login"""
      return self._logs[len(self._logs)-1]

   def logins (self):
      """Return list of all logins"""
      return [i for i, o in pairwise(self._logs) ]

   def logouts (self):
      """Return list of all logouts"""
      return [o for i, o in pairwise(self._logs) ]

   def logs (self, fmt = None):
      """Return list of logs"""
      if fmt:
         return [ i.strftime(fmt) for i in self._logs]
      else:
         return self._logs

def main():

   d = DayLog()
   print(d)

   d = DayLog(datetime.datetime.today(), ['09:03', '10:13'])
   print (d)

   d1 = DayLog(datetime.datetime.today(), ['09:03', '10:13'])
   d2 = DayLog(datetime.datetime.today(), ['11:03', '12:13'])

   #print(d1)
   #print(d2)
   print(d1+d2)


if __name__ == '__main__':
    main()

