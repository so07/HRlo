#!/usr/bin/env python3
import datetime
import argparse

from .logs.dayutils import day_range as DayRange
from .logs.dayutils import week_bounds, month_bounds

from . import HRauth
from . import HRget
from . import HRday
from . import HRdayList
from . import HRphone
from . import HRpresence
from . import HRtotalizator

from . import color
from . import config as HRconfig


class HRlo(object):


   def __init__(self, auth, config = {}, day_range=None):

       self.hr_auth = auth
       self.hr_get = HRget.HRget(self.hr_auth)

       self.days = [] # initialization in init_data

       self.config = {}
       self.config.update( config )


   def __str__ (self):
       s = ''
       for i in self.days:
           s += str(i) + '\n'
       return s


   def __getitem__(self, key):
       if not self.days:
           raise KeyError("no data for {}".format(key))
       if not isinstance(key, datetime.datetime) and \
          not isinstance(key, datetime.date) and \
          not isinstance(key, DayRange) and \
          not isinstance(key, slice):
          print("@__getitem__ NOT datetime.datetime")
          return None
       if isinstance(key, DayRange):
          l = [ d for d in self.days if d.day().date() in key ]
          return l
       elif isinstance(key, datetime.datetime):
          l = [ d for d in self.days if d.day().date() == key.date() ]
          return l
       elif isinstance(key, datetime.date):
          l = [ d for d in self.days if d.day().date() == key ]
          return l
       elif isinstance(key, slice):
          return self.days[key.start.day-1:key.stop.day-1]
       else:
          return self.days[key.day-1]


   def init_data(self, day_range=None):
       if day_range:
          json = self.hr_get.get_range(day_range)
       else:
          json = self.hr_get.get()

       self.days = [ HRday.HRday({'Fields':json['Fields'], 'Data':d}) for d in json['Data'] ]


   def report_day(self, day = datetime.date.today()):
       """Return report for a day.
          Return a HRday class."""
       self.init_data( DayRange(day, day) )
       return self


   def report_week(self, day = datetime.datetime.today()):
       """Return report for a week.
          Return a HRdayList class."""
       start, end = week_bounds(day)
       # check if week start and end are inside current month
       month_limits = month_bounds(day)
       start = max(start, month_limits[0])
       end = min(end, month_limits[1])
       return self.report(start, end, label="Weekly report")


   def report_month(self, day = datetime.datetime.today()):
       """Return report for a month.
          Return a HRdayList class."""
       start, end = month_bounds(day)
       return self.report(start, end, label="Monthly report")


   def report(self, start, end, label=''):
       """Return report for a time interval.
          Return a HRdayList class."""
       day_range = DayRange(start, end)

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
       _anomalies = [d for d in self.days if d.anomaly()]
       if _anomalies:
           col = color.color(color.RED)( str )
           warning = "WARNING : {} anomalies found : {}".format(len(_anomalies),  [ str(d.day().date()) for d in _anomalies ] )
           print( col(warning) )
       return _anomalies


   def phone(self, names=[], phones=[]):
       djson = self.hr_get.phone()
       hr_phone = HRphone.HRphone(djson)
       return hr_phone.report(names, phones)


   def presence(self, surname):
       csv_data = self.hr_get.presence()
       hr_presence = HRpresence.HRpresence(csv_data)
       return hr_presence.report(surname)


   def totalizator(self, key=None):
       hr_totalizator = HRtotalizator.HRtotalizator(self.hr_get.totalizators())
       if key:
           return hr_totalizator.get_value(key)
       else:
           return hr_totalizator.report()



def main():

   parser = argparse.ArgumentParser(prog='HRlo (aka accaerralo)',
                                    description='HR manager.',
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

   HRphone.add_parser(parser)

   HRtotalizator.add_parser(parser)

   HRauth.add_parser(parser)

   args = parser.parse_args()


   config = {'today' : args.today}

   #config = {}

   hr_auth = HRauth.HRauth(**vars(args))

   hr = HRlo(hr_auth, config)

   if args.from_day and args.to_day:
      print(hr.report(args.from_day, args.to_day))

   if args.daily:
      print(hr.report_day())

   if args.weekly:
      print(hr.report_week())

   if args.monthly:
      print(hr.report_month())

   if args.phone_name or args.phone_number:
       print(hr.phone(names = args.phone_name, phones = args.phone_number))

   if  args.presence:
       print(hr.presence(args.presence))

   if args.totalizators or args.get_totalizator:
       print(hr.totalizator(args.get_totalizator))

   if not args.daily and not args.weekly and not args.monthly \
      and not args.from_day \
      and not args.phone_name and not args.phone_number and not args.presence \
      and not args.totalizators and not args.get_totalizator:
      today = hr.report_day()
      if today:
          print("\nToday :")
          print(today)


if __name__ == '__main__':
   main()

