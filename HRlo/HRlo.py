#!/usr/bin/env python3
import re
import sys
import datetime
import argparse

from .logs.dayutils import dayutils
from .utils import NameParser

from . import HRauth
from . import HRget
from . import HRday
from . import HRdayList
from . import HRpresence
from . import HRtotalizator

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

       # check if week start and end are inside current month
       month_bounds = dayutils.month_bounds(day)
       start = max(start, month_bounds[0])
       end = min(end, month_bounds[1])

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

   def get_phone(self, surname):
       return self.hrget.phone(surname)

   def get_presence(self, surname):
       csv_data = self.hrget.presence()
       presence = HRpresence.HRpresence(csv_data)
       return presence.report(surname)

   def get_totalizator(self, key=None):
       hr_tot = HRtotalizator.HRtotalizator(self.hrget.totalizators())
       if key:
           return hr_tot.get_value(key)
       else:
           return hr_tot.report()


def main():

   parser = argparse.ArgumentParser(prog='HRlo (aka accaerralo)',
                                    description='',
                                    formatter_class=argparse.RawTextHelpFormatter)

   parser.add_argument('--version', action='version',
                       version='%(prog)s ' + HRconfig.version,
                       help='print version and exit')


   parser_todo = parser.add_argument_group('report options')

   parser_todo.add_argument('-d', '--daily',
                            action='store_true',
                            help='daily report')

   parser_todo.add_argument('-w', '--weekly',
                            action='store_true',
                            help='weekly report')

   parser_todo.add_argument('-m', '--monthly',
                            action='store_true',
                            help='monthly report')

   parser_todo.add_argument('-t', '--today',
                            action='store_true',
                            help='keep today in reports')


   parser_range = parser.add_argument_group('range days options')

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
                             help="from date YYYY-MM-DD")

   parser_range.add_argument("--to",
                             dest = 'to_day',
                             type=_date,
                             #default=None,
                             default=datetime.date.today(),
                             metavar="YYYY-MM-DD",
                             help="to date YYYY-MM-DD (default %(default)s)")

   HRpresence.add_parser(parser)

   HRget.add_parser_phone(parser)

   HRtotalizator.add_parser(parser)

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

   if args.phone_name or args.phone_number:
       djson = hr.hrget.phone(names = args.phone_name, phones = args.phone_number)
       print()
       for d in djson['Data']:
           for k, v in zip(djson['Fields'], d):
               print(v)
           print()

   if args.presence:
      for name in args.presence:
          p = hr.get_presence(name)
          print(p)

   if args.totalizators or args.get_totalizator:
       print(hr.get_totalizator(args.get_totalizator))

   if not args.daily and not args.weekly and not args.monthly \
      and not args.from_day \
      and not args.phone_name and not args.phone_number and not args.presence \
      and not args.totalizators and not args.get_totalizator:
      today = hr.get_report_day()
      if today:
          print("\nToday :")
          print(today)


if __name__ == '__main__':
   main()

