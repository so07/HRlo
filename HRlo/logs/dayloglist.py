#!/usr/bin/env python3
import datetime

import dayutils

from daylog import DayLog

class DayLogList(list, DayLog):

    def __init__(self):
       self._uptime = datetime.timedelta(0)

    def __str__(self):
       s = ''
       s += "[LIST] "
       s += "{:.<20}".format("Date")
       s += "{}\n".format( ", ".join([ i.date() for i in self ]))

       s += " "*7 + "{:.<20}".format("Up")
       s += "{}\n".format( ", ".join([ dayutils.sec2str(i.uptime().total_seconds()) for i in self ]))

       s += " "*7 + "{:.<20}".format("Logs")
       for j in self:
          s += "[{}] ".format(", ".join([ i.time().strftime(dayutils.fmt_time) for i in j.logs() ]))
       s += '\n'

       s += " "*7 +  "{:.<20}{}\n".format( 'Uptime', dayutils.sec2str(self._uptime.total_seconds()) )

       return s

    def append(self, args):
       list.append(self, args)
       self._uptime += args._uptime


def main():
   d1 = DayLog(datetime.datetime(2014, 12, 3), ['09:03', '10:13'])
   print(d1)
   d2 = DayLog(datetime.datetime(2014, 12, 4), ['11:03', '15:13'])
   l = DayLogList()
   print(l)
   l.append(d1)
   #print(l)
   l.append(d2)
   print(l)


if __name__ == '__main__':
   main()
