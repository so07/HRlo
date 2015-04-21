#!/usr/bin/env python3
import re
import sys
import datetime

from HRlo.logs import dayutils

from . import HRauth
from . import HRget
from . import HRday
from . import HRdayList

from . import color
from . import config as HRconfig

class HRlo(object):

   def __init__(self, dauth, config = {}, day_range=None):
       self.auth = HRauth.HRauth(**dauth)
       self.hrget = HRget.HRget(self.auth)

       self.data = None

       self.day_range = day_range

       self.config = {}
       self.config.update( config )

   def __str__ (self):
       s = ''
       for i in self.data:
           s += str(i) + '\n'
       return s

   def __getitem__(self, key):
       if not self.data:
           raise KeyError("no data for {}".format(key))
       if not isinstance(key, datetime.datetime) and \
          not isinstance(key, datetime.date) and \
          not isinstance(key, dayutils.day_range) and \
          not isinstance(key, slice):
          print("@__getitem__ NOT datetime.datetime")
          return None
       if isinstance(key, dayutils.day_range):
          l = [ d for d in self.data if d.day().date() in key ]
          return l
       elif isinstance(key, datetime.datetime):
          l = [ d for d in self.data if d.day().date() == key.date() ]
          return l
       elif isinstance(key, datetime.date):
          l = [ d for d in self.data if d.day().date() == key ]
          return l
       elif isinstance(key, slice):
          #print( key.start.day-1, key.stop.day-1)
          return self.data[key.start.day-1:key.stop.day-1]
       else:
          return self.data[key.day-1]


   def init_data(self, day_range=None):
       if day_range:
          json = self.hrget.get_range(day_range)
       else:
          json = self.hrget.get()

       fields, HRdata = json['Fields'], json['Data']
       self.data = [ HRday.HRday(fields, day) for day in HRdata]


   def get_report_day(self, day = datetime.date.today()):
       self.init_data( dayutils.day_range(day, day) )
       return self


   def get_report_week(self, day = datetime.datetime.today()):

       start, end = dayutils.week_bounds(day)

       return self.get_report(start, end, label="Weekly report")


   def get_report_month(self, day = datetime.datetime.today()):

       start, end = dayutils.month_bounds(day)

       return self.get_report(start, end, label="Monthly report")


   def get_report(self, start, end, label = ''):

       day_range = dayutils.day_range(start, end)

       self.init_data(day_range)

       if start == end:
           _label = str(start)
       else:
           _label = "From {} To {}".format( str(start), str(end) )

       if label:
           _label = "{} : {}".format( label, _label)

       l = HRdayList.HRdayList(label=_label)
       for i in self[day_range]:
           if i.is_today() and not self.config.get('today', False): continue
           l.append(i)
       return l


   def anomalies(self):
       _anomalies = [d for d in self.data if d.anomaly()]
       if _anomalies:
           col = color.color(color.RED)( str )
           warning = "WARNING : {} anomalies found : {}".format(len(_anomalies),  [ str(d.day().date()) for d in _anomalies ] )
           print( col(warning) )
       return _anomalies

   def get_report_all(self):

       day = self.get_report_day()
       #print(day)
       week = self.get_report_week()
       #print(week)
       month = self.get_report_month()
       #print(month)

       return day, week, month

   def report(self):
       d, w, m = self.get_report_all()
       print(d)
       print(w)
       print(m)


def debug():

    hrlo = HRlo()

    #print(hrlo)

    hrlo.report()


def main():

   import argparse
   import getpass

   parser = argparse.ArgumentParser(prog='HRlo (aka accaerralo)',
                                    description='',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter
                                   )


   parser_todo = parser.add_argument_group()

   parser_todo.add_argument('-d', '--daily',
                            action='store_true',
                            help='Daily report')

   parser_todo.add_argument('-w', '--weekly',
                            action='store_true',
                            help='Weekly report')

   parser_todo.add_argument('-m', '--monthly',
                            action='store_true',
                            help='Monthly report')

   parser_todo.add_argument('-t', '--today',
                            action='store_true',
                            help='Keep today in reports')


   parser_range = parser.add_argument_group()

   def _date(s):
      for fmt in ['%Y-%m-%d', '%Y%m%d', '%d-%m-%Y', '%d/%m/%Y']:
         try:
            return datetime.datetime.strptime(s, fmt).date()
         except:
            pass
      raise ValueError("invalid date {}".format(s))

   parser_range.add_argument("--from",
                             dest = 'from_day',
                             type=_date,
                             default=None, #default=datetime.datetime(1970, 1, 1),
                             metavar="YYYY-MM-DD",
                             help="From date YYYY-MM-DD")

   parser_range.add_argument("--to",
                             dest = 'to_day',
                             type=_date,
                             default=None, #default=datetime.datetime.today(),
                             metavar="YYYY-MM-DD",
                             help="To date YYYY-MM-DD")

   parser_other = parser.add_argument_group()

   parser_other.add_argument('--version', action='version',
                             version='%(prog)s ' + HRconfig.version,
                             help='Print version')

   dauth = HRauth.add_parser(parser)

   args = parser.parse_args()

   config = {'today' : args.today}

   #config = {}

   hr = HRlo(dauth, config)

   if args.from_day and args.to_day:
      print(hr.get_report(args.from_day, args.to_day))

   if args.daily:
      print(hr.get_report_day())

   if args.weekly:
      print(hr.get_report_week())

   if args.monthly:
      print(hr.get_report_month())

   if not args.daily and not args.weekly and not args.monthly \
      and not args.from_day and not args.to_day:
      print("\nToday :")
      print(hr.get_report_day())


if __name__ == '__main__':
   main()
   #debug()
