#!/usr/bin/env python3
import datetime
import dayutils

from daylog import DayLog

class DayLogList(list):

    def __init__(self):
       self.daylog = DayLog()

    def __str__(self):

       s = "[LIST] "

       # date
       s += "{:.<20}".format("Date")
       s += "{}\n".format( ", ".join([ i.date(True) for i in self ]))

       # uptime per day
       s += " "*7 + "{:.<20}".format("Up")
       s += "{}\n".format( ", ".join([ dayutils.sec2str(i.uptime().total_seconds()) for i in self ]))

       # logs
       s += " "*7 + "{:.<20}".format("Logs")
       for j in self:
          s += "[{}] ".format(", ".join([ i.time().strftime(dayutils.fmt_time) for i in j.logs() ]))
       s += '\n'

       # uptime
       s += " "*7 +  "{:.<20}{}\n".format( 'Uptime', dayutils.sec2str(self.daylog.uptime().total_seconds()) )

       return s

    def append(self, args):
       list.append(self, args)
       self.daylog['uptime'] += args['uptime']

