#!/usr/bin/env python3
import re
import sys
import datetime
import argparse

import dayutils
import daylog

class Logs:

   string_in  = 'IN'
   string_out = 'OUT'

   # private method {{{

   def _get_data_from_files(self):
      data = ''
      for file_log in self._files:
         with open(file_log, "r") as f:
             data += f.read()
      return data

   def _get_extreme_days_from_data(self):
      # get first day of list
      day_id = self._data.split('\n')[ 0].split()[1]
      start = dayutils.str2day(day_id)
      # get last day of list
      day_id = self._data.split('\n')[-2].split()[1]
      end = dayutils.str2day(day_id)
      return start, end


   def _get_logs_from_data(self):
      l = []
      # iterate over days from first to last
      #for d in self._day_start.dayrange(self._day_final):
      for d in dayutils.day_range(self._day_start, self._day_final ):
          logs_day = re.findall('.*'+str(d.strftime(dayutils.fmt_id))+'.*', self._data)
          num_login  = len(re.findall(self.string_in,  " ".join(logs_day)))
          num_logout = len(re.findall(self.string_out, " ".join(logs_day)))

          # if number of login/logout is the same and at least one login
          if num_login and (num_login == num_logout):
              # get only time
              logs_day = [ i.split()[2] for i in logs_day]
              l.append( daylog.DayLog(d, logs_day) )

      # sort logs by decreasing uptime
      l.sort(key = lambda x : x.uptime(), reverse = True)
      return l

   # }}}

   def __init__(self, list_of_file = []):

      # list of log files
      self._files = list_of_file

      # data logs
      self._data = self._get_data_from_files()

      # first and last day
      self._day_start, self._day_final = self._get_extreme_days_from_data()

      # list of day logs (list of DayLog class)
      self._logs = self._get_logs_from_data()


   def __str__(self):
       #def _str(k, v):
       #   return "%s %s\n" % ( k.ljust(30, '.'), v )
       #s = ''
       #s += _str("Read data from file", ", ".join(self._files))
       #s += _str("First day", self._day_start)
       #s += _str("Last day", self._day_final)
       #s += _str("Number of days", self.num_days_total())
       #s += _str("Number of working days", str(self.num_days_work()) + ' (%.0f%%)' % (100.0*self.num_days_work()/self.num_days_total())) 
       #return s
      return self.report()

   def report(self):
      def _str(k, v):
         return "%s %s\n" % ( k.ljust(30, '.'), v )
      s = '\n'
      s += _str("Read data from file", ", ".join(self._files))
      s += _str("First day", self._day_start)
      s += _str("Last day", self._day_final)

      s += _str("Number of days", self.num_days_total())
      s += _str("Number of working days", str(self.num_days_work()) + ' (%.0f%%)' % (100.0*self.num_days_work()/self.num_days_total())) 

      s += _str( "Working time total", self.uptime_total() )
      d = self.uptime_max()
      s += _str( "Working time max", "%s @ %s" % ( str(d.uptime()), str(d.date()) ) )
      d = self.uptime_min()
      s += _str( "Working time min", "%s @ %s" % ( str(d.uptime()), str(d.date()) ) )
      s += _str( "Working time average", self.uptime_mean() )

      # get most prolific week day
      p = self.get_max_uptime_by_day()
      s += _str( "Most prolific week day", dayutils.days_long[ p[1] ] + " (" + str(p[0]) + " working time)")
      # get most prolific month
      p = self.get_max_uptime_by_month()
      s += _str( "Most prolific month", dayutils.months_long[ p[1] ] + " (" + str(p[0]) + " working time)")
      # get most prolific year
      p = self.get_max_uptime_by_year()
      s += _str( "Most prolific year",  str(p[1]) + " (" + str(p[0]) + " working time)")

      return s


   def num_days_total(self):
      """Return total number of days between start and end days"""
      return (self._day_final - self._day_start).days
   def num_days_work(self):
      """Return number of working days between start and end days"""
      return len(self._logs)

   def days_first(self):
      """Return first day"""
      return self._day_start
   def days_last(self):
      """Return last day"""
      return self._day_final


   def uptime_max(self):
      """Return maximum uptime"""
      return self._logs[0]
   def uptime_min(self):
      """Return minimum uptime"""
      return self._logs[-1]

   def uptime_total(self):
      """Return total uptime"""
      up = self.get_from_logs('uptime')
      t = datetime.timedelta(0)
      for i in up:
          t += i
      return t

   def uptime_mean(self):
      """Return mean uptime for day"""
      up = self.uptime_total()
      wd = self.num_days_work()
      return up/wd


   def get_from_logs(self, attribute):
      """Return a list with attribute from daylogs"""
      return [ getattr(i, attribute)() for i in self._logs ]


   def get_logs(self, condition = lambda x : True):
      """Return logs. If condition is specified return a list of logs satisfying the condition"""
      if condition:
         return [ i for i in self._logs if condition(i) ]
         #return sorted([ getattr(i, function)() for i in self._logs if condition(i) ])
      else:
         return self._logs

   def sort_logs(self, attribute, reverse = False):
      """Sort logs by attribute"""
      return sorted( self._logs, key = lambda x : getattr(x, attribute)(), reverse = reverse)

   def get_day(self, day):
      """Return a list of daylogs with specified day of month"""
      return self.get_logs(lambda x : x.day().day == day)
   def get_weekday(self, weekday):
      """Return a list of daylogs with specified day of week"""
      return self.get_logs(lambda x : x.day().weekday() == weekday)
   def get_month(self, month):
      """Return a list of daylogs with specified month"""
      return self.get_logs(lambda x : x.day().month == month)
   def get_year(self, year):
      """Return a list of daylogs with specified year"""
      return self.get_logs( lambda x : x.day().year == year)

   def login_early(self):
      """Return earliest login"""
      return self.sort_logs('login')[0]
   def login_last(self):
      """Return latest login"""
      return self.sort_logs('login', True)[0]

   def logout_early(self):
      """Return earliest logout"""
      return self.sort_logs('logout')[0]
   def logout_last(self):
      """Return latest logout"""
      return self.sort_logs('logout', True)[0]

   def daylog_sum(self, l):
      """Return the sum of a list of daylogs"""
      s = daylog.DayLog()
      for i in l:
          s += i
      return s


   def get_logs_by (self, function, ranges):
      """Return a list (with length of ranges) of a list of daylogs that satisfy : function() == index of ranges"""
      return [ [j for j in getattr(self, function)(i) ] for i in ranges]

   def get_uptime_by_day(self, ranges = range(7)):
      """Return a list of list of daylogs accordling to weekday index.
      Default day ranges [0:7].
      0 is Monday
      [ [Mondays], [Tuesdays], ... , [Sundays] ]"""
      # return a list of list of DayLog with all days devided by week day
      # [ [Mondays], [Tuesdays], ... , [Sundays] ]
      l = self.get_logs_by('get_weekday', ranges)
      # return uptime of DayLogs sum
      return  [ self.daylog_sum(i).uptime() for i in l]

   def get_uptime_by_month(self, ranges = range(1, 13)):
      """Return a list of list of daylogs accordling to month index of ranges.
      Default month ranges [1:13].
      1 is January"""
      # return a list of list of DayLog devided by month
      l =  self.get_logs_by('get_month', ranges)
      # return uptime of DayLogs sum
      return  [ self.daylog_sum(i).uptime() for i in l]

   def get_uptime_by_year(self, ranges = range(0, datetime.datetime.today().year)):
      """Return a list of list of daylogs accordling to year index of ranges.
      Default year ranges [0:taday's year]."""
      # return a list of list of DayLog devided by year
      l =  self.get_logs_by('get_year', ranges)
      # return uptime of DayLogs sum
      return  [ self.daylog_sum(i).uptime() for i in l]



   def get_uptime_by(self, logs_function, search_function):
      """Return uptime and index of uptime accordingly to logs_function and search_function"""
      l = getattr(self, logs_function)()
      uptime = search_function(l)
      index  = l.index(uptime)
      return uptime, index

   def get_max_uptime_by_day(self):
      """Return max uptime and day of max uptime between total uptime of all weekday"""
      return self.get_uptime_by('get_uptime_by_day', max)
   def get_max_uptime_by_month(self):
      """Return max uptime and month of max uptime between total uptime of all month"""
      return self.get_uptime_by('get_uptime_by_month', max)
   def get_max_uptime_by_year(self):
      """Return max uptime and year of max uptime between total uptime of all year"""
      return self.get_uptime_by('get_uptime_by_year', max)


def main():

   parser = argparse.ArgumentParser(prog='',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

   parser.add_argument('--report',
                       action='store_true',
                       help='print report')

   parser.add_argument('--days-tot',
                       dest='num_days_total',
                       action='store_true',
                       help='number of total days')
   parser.add_argument('--days-work',
                       dest='num_days_work',
                       action='store_true',
                       help='number of working days')
   parser.add_argument('--days-first',
                       dest='days_first',
                       action='store_true',
                       help='first day')
   parser.add_argument('--days-last',
                       dest='days_last',
                       action='store_true',
                       help='last day')


   parser.add_argument('--uptime-tot',
                       dest='uptime_total',
                       action='store_true',
                       help='minimum uptime')
   parser.add_argument('--uptime-max',
                       action='store_true',
                       help='maximum uptime')
   parser.add_argument('--uptime-min',
                       action='store_true',
                       help='minimum uptime')
   parser.add_argument('--uptime-mean',
                       action='store_true',
                       help='mean uptime for working days')


   parser.add_argument('--login-early',
                       action='store_true',
                       help='earlier login')
   parser.add_argument('--login-last',
                       action='store_true',
                       help='latest login')
   parser.add_argument('--logout-early',
                       action='store_true',
                       help='earlier logout')
   parser.add_argument('--logout-last',
                       action='store_true',
                       help='latest logout')

   # Positional parameters (Files)
   parser.add_argument('files',
                       nargs='+',
                       help = "File [File ... ]")

   args = parser.parse_args()

   a = Logs(args.files)

   #print a

   for k, v in sorted(vars(args).items()):
       if v and isinstance(v, bool):
          d = getattr(a, k)()
          if d:
             print( "%s : %s" % (re.sub('_', ' ', k).ljust(15), d) )

   #for i in a.get_logs():
   #   print( i.uptime(), i.date() )

   print( a.report())


if __name__ == '__main__':
    main()
