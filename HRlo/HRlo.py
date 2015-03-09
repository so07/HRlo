#!/usr/bin/env python3
import re
import sys
import datetime

from logs import dayutils

import HRauth
import HRget
import HRday
import HRdayList


class HRlo(object):

   def __init__(self, auth):
       hrget  = HRget.HRget(auth)
       fields, HRdata = hrget.get()
       self.data = [ HRday.HRday(fields, day) for day in HRdata]

       anomalies = self.anomalies()
       if anomalies:
           print("WARNING : {} anomalies found : {}".format(len(anomalies),  [ str(d.day().date()) for d in anomalies ] ))

   def __str__ (self):
       s = ''
       for i in self.data:
           s += str(i) + '\n'
       return s

   def __getitem__(self, key):
       #print( type(key))
       if not isinstance(key, datetime.datetime) and \
          not isinstance(key, datetime.date) and \
          not isinstance(key, slice):
          print("@__getitem__ NOT datetime.datetime")
          return None
       if isinstance(key, slice):
          #print( key.start.day-1, key.stop.day-1)
          return self.data[key.start.day-1:key.stop.day-1]
       else:
          return self.data[key.day-1]

   def get_report_day(self, day = datetime.datetime.today()):
       d = self[day]
       d.label = "Dayly report : " + str(day.date())
       return d

   def get_report_week(self, day = datetime.datetime.today()):
       start, end = dayutils.week_bounds(day)

       label = "Weekly report : From " + str(start) + " To " + str(end)

       l = HRdayList.HRdayList(label=label)
       for i in self[start:end]:
           l.append(i)
       return l

   def get_report_month(self, day = datetime.datetime.today()):

       start, end = dayutils.month_bounds(day)

       label = "Monthly report : From " + str(start) + " To " + str(end)

       l = HRdayList.HRdayList(label=label)
       for i in self[start:end]:
           l.append(i)
       return l

   def anomalies(self):
       return [d for d in self.data if d.anomaly()] 

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
                                    #formatter_class=argparse.ArgumentDefaultsHelpFormatter
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

   HRauth.add_parser(parser)

   args = parser.parse_args()

   args.password = getpass.getpass()

   dargs = vars(args)

   #print(args)

   auth = HRauth.HRauth(dargs['host'], dargs['username'], dargs['idemploy'], dargs['password'])

   hr = HRlo(auth)

   if args.daily:
      print(hr.get_report_day())

   if args.weekly:
      print(hr.get_report_week())

   if args.monthly:
      print(hr.get_report_month())

   if not args.daily and not args.weekly and not args.monthly:
      print("\nToday :")
      print(hr[datetime.datetime.today()])


if __name__ == '__main__':
   main()
   #debug()
