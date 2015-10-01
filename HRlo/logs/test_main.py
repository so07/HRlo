#!/usr/bin/env python3
import re
import datetime

from daylog import DayLog
from dayloglist import DayLogList

def main():

   print("\n>>> DayLog tests:")

   print(">>> Null DayLog")

   d = DayLog()
   print(d)

   print(">>> Today DayLog")

   d = DayLog(datetime.datetime.today(), ['09:03', '10:13'])
   print (d)

   print(">>> date()")
   print(d.date())
   print(">>> uptime()")
   print(d.uptime())

   print(">>> logins()")
   print(d.logins())
   print(">>> logouts()")
   print(d.logouts())

   d1 = DayLog(datetime.datetime.today(), ['09:03', '10:13'])
   d2 = DayLog(datetime.datetime.today(), ['11:03', '12:13'])

   print(">>> Sum")
   print(">>> d1")
   print(d1)
   print(">>> d2")
   print(d2)

   s = d1+d2

   print(">>> d1 + d2")
   print(s)

   #print(s.logins())


   print("\n>>> DayLogList tests:")

   print(">>> DayLogList null")
   l = DayLogList()
   print(l)

   print(">>> d1")

   d1 = DayLog(datetime.datetime(2014, 12, 3), ['09:03', '10:13'])
   print(d1)

   print(">>> d2")

   d2 = DayLog(datetime.datetime(2014, 12, 4), ['11:03', '15:13'])
   print(d2)

   l.append(d1)
   #print(l)
   l.append(d2)

   print(">>> d1 + d2")
   print(l)


if __name__ == '__main__':
    main()

