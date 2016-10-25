#!/usr/bin/env python3
import datetime
import argparse

from .logs.dayutils import day_range as DayRange
from .logs.dayutils import week_bounds, month_bounds, month_weeks_bounds

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


   def day(self, day = datetime.date.today()):
       """Return HRday class for a day."""
       self.init_data( DayRange(day, day) )
       return self


   def week(self, day = datetime.datetime.today()):
       """Return HRdayList class for a week."""
       start, end = week_bounds(day)
       # check if week start and end are inside current month
       month_limits = month_bounds(day)
       start = max(start, month_limits[0])
       end = min(end, month_limits[1])
       return self.get(start, end, label="Weekly report", overtime=self.config.get('overtime', 0))


   def month(self, day = datetime.datetime.today()):
       """Return HRdayList for a month."""
       start, end = month_bounds(day)
       return self.get(start, end, label="Monthly report")


   def month_weeks(self, day = datetime.datetime.today()):
       """Return a list of HRdayList for month weeks."""
       _hrdaylist = []
       # get month bounds
       month_limits = month_bounds(day)
       # get today bound
       after_bound = datetime.datetime.today().date()
       if not self.config.get('today', True):
           # get yesterday as bound
           after_bound = datetime.datetime.today().date() - datetime.timedelta(days=1)
       for w in month_weeks_bounds(day):
           start = w[0]
           if start > after_bound:
               break
           # check if week end are inside current month
           end = min(w[1], month_limits[1])
           # check if week end are after today
           end = min(end, after_bound)
           # get HRdayList for this week
           _hrdaylist.append(self.get(start, end, overtime=self.config.get('overtime', 0)))
       return _hrdaylist


   def get(self, start, end, label='', overtime=0):
       """Return HRdayList for a day interval."""
       day_range = DayRange(start, end)

       self.init_data(day_range)

       if start == end:
           _label = str(start)
       else:
           _label = "From {} To {}".format( str(start), str(end) )

       if label:
           _label = "{} : {}".format( label, _label)

       l = HRdayList.HRdayList(label=_label, overtime=overtime)
       for i in self[day_range]:
           if i.is_today() and not self.config.get('today', False): continue
           l.append(i)

       return l


   def report(self, start, end):
       return str(self.get(start, end))


   def report_day(self, day = datetime.date.today()):
       """Return report from HRday class for a day."""
       return str(self.day(day))


   def report_week(self, day = datetime.datetime.today()):
       """Return report from HRdayList class for a week."""
       return str(self.week(day))


   def report_month(self, day = datetime.date.today()):
       """Return report from HRdayList class for a month."""
       return str(self.month(day))


   def report_month_weeks(self, day = datetime.date.today()):
       """Return report from HRdayList class for a month."""
       return "\n".join([ str(w) for w in self.month_weeks(day)])


   def report_keys(self, keys = [], from_day = datetime.date(datetime.date.today().year, 1, 1), to_day = datetime.date.today()):
       """Return keys report from HR time of HRdayList class for day range."""
       l = self.get(from_day, to_day)
       t = datetime.timedelta(0)
       days = []
       for d in l:
           for k in keys:
               _time = d._get_hr_time(k)
               t += _time
               if _time:
                   days.append(d)
       if self.config.get('verbose'):
           if days:
               print("number of days =", len(days))
               print("days =", ", ".join([str(d['date'].date()) for d in days]))
       return t


   def anomalies(self):
       _anomalies = [d for d in self.days if d.anomaly()]
       if _anomalies:
           col = color.color(color.RED)( str )
           warning = "WARNING : {} anomalies found : {}".format(len(_anomalies),  [ str(d.day().date()) for d in _anomalies ] )
           print( col(warning) )
       return _anomalies


   def phone(self, names=[], phones=[]):
       """Return report of names and phone numbers from HRphone class."""
       djson = self.hr_get.phone()
       hr_phone = HRphone.HRphone(djson)
       return hr_phone.report(names, phones)


   def presence(self, surname):
       """Return report of workers presence from HRpresence class."""
       csv_data = self.hr_get.presence()
       hr_presence = HRpresence.HRpresence(csv_data)
       return hr_presence.report(surname)


   def totalizator(self, key=None):
       """Return report of totalizators from HRtotalizator class."""
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

   parser.add_argument('-v', '--verbose',
                       action="count", default=0,
                       help="increase verbosity")

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

   parser_todo.add_argument('-M', '--week-monthly',
                            action='store_true',
                            help='monthly report week by week')

   parser_todo.add_argument('-t', '--today',
                            action='store_true',
                            help='keep today in reports')

   parser_todo.add_argument('-o', '--overtime',
                            type=int,
                            default=0,
                            help='overtime hours. Remove overtime from timenets. Only supported in weekly and month week by week report. (default %(default)s)')

   parser_todo.add_argument('--report-keys',
                            nargs='+',
                            help='report on HR keys. By default report starts from first day of current year until today. Otherwise use --from and --to options to define time range')


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
                             default=datetime.date.today(),
                             metavar="YYYY-MM-DD",
                             help="to date YYYY-MM-DD (default %(default)s)")

   HRpresence.add_parser(parser)

   HRphone.add_parser(parser)

   HRtotalizator.add_parser(parser)

   HRauth.add_parser(parser)

   args = parser.parse_args()


   config = {'today' : args.today, 'overtime' : args.overtime, 'verbose' : args.verbose}

   hr_auth = HRauth.HRauth(**vars(args))

   hr = HRlo(hr_auth, config)


   if args.from_day and args.to_day and not args.report_keys:
       print(hr.report(args.from_day, args.to_day))

   if args.daily:
       print(hr.report_day())

   if args.weekly:
       print(hr.report_week())

   if args.monthly:
       print(hr.report_month())

   if args.week_monthly:
       print(hr.report_month_weeks())

   if args.phone_name or args.phone_number:
       print(hr.phone(names = args.phone_name, phones = args.phone_number))

   if args.presence:
       print(hr.presence(args.presence))

   if args.totalizators or args.get_totalizator:
       print(hr.totalizator(args.get_totalizator))

   if args.report_keys:
       if args.from_day and args.to_day:
           print(hr.report_keys(args.report_keys, args.from_day, args.to_day))
       elif not args.from_day and args.to_day:
           print(hr.report_keys(args.report_keys, to_day=args.to_day))
       else:
           print(hr.report_keys(args.report_keys))

   if not args.daily and not args.weekly and not args.monthly and not args.week_monthly \
      and not args.from_day \
      and not args.phone_name and not args.phone_number and not args.presence \
      and not args.totalizators and not args.get_totalizator and not args.report_keys:
      today = hr.report_day()
      if today:
          print("\nToday :")
          print(today)


if __name__ == '__main__':
   main()

