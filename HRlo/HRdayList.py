#!/usr/bin/env python3
import datetime

from logs import dayutils

from HRday import HRday

class HRdayList(list, HRday):

    def __init__(self, label = None):
       self._uptime  = datetime.timedelta(0)
       self._timenet = 0

       self.label = label

       self._days = HRday()

    def __str__(self):
       s = ''

       if self.label:
          s += "."*20 + "{}\n".format(self.label)

       s += "{:.<20}".format("Working days")
       s += "{}\n".format( ", ".join([ str(i.day().date()) for i in self if i.is_working()]))
       s += "{:.<20}".format("Num. Working days")
       s += "{}\n".format( self.working_days_number() )
       #s += "{:.<20}".format("Working days list")
       #s += "{}\n".format( self.working_days_list() )
       s += "{:.<20}".format( "Uptime" )
       s += "{}\n".format( dayutils.sec2str(self._uptime.total_seconds()) )
       s += "{:.<20}".format( "Uptime mean" )
       s += "{}\n".format( dayutils.sec2str(self.uptime_mean().total_seconds()) )
       s += "{:.<20}".format( "Timenet" )
       s += "{}\n".format( dayutils.sec2str(self.timenet()) )
       s += "{:.<20}".format( "Timenet mean" )
       s += "{}\n".format( dayutils.sec2str(self.timenet_mean()) )
       #s += "{:.<20}".format("Logs")
       #for j in self:
       #   s += "[{}] ".format(", ".join([ i.time().strftime(dayutils.fmt_time) for i in j.logs() ]))
       #s += '\n'

       s += "{:.<20}".format("Timenets")
       s += "[{}]\n".format( ", ".join([ dayutils.sec2str(d.timenet()) for d in self if d.is_working()]) )

       s += "{:.<20}".format( "Anomaly" )
       s += "{}\n".format( self.anomaly() )

       #s += "\n" + str(self._days) + '\n'

       return s

    def append(self, args):
       #if not args.is_working(): return
       list.append(self, args)
       self._uptime += args._uptime
       if not args.anomaly() and not args.is_holiday():
          self._timenet += args._timenet
       self._days += args

    def _getattr_from_HRday(self, attr):
       return [getattr(i, attr)() for i in self]

    def uptime_list(self):
       return self._getattr_from_HRday('uptime') 
    def uptime(self):
       up = datetime.timedelta(0)
       for i in self.uptime_list():
          up += i
       return up 

    def anomaly_list(self):
       return self._getattr_from_HRday('anomaly') 
    def anomaly(self):
       return sum(self.anomaly_list())

    #def timenet_list(self):
    #   return self._getattr_from_HRday('timenet')
    #def timenet(self):
    #   return sum(self.timenet_list())

    def is_working_list(self):
       return self._getattr_from_HRday('is_working')

    def working_days_number(self):
       return sum(self.is_working_list())
    def working_days_list(self):
       return [ i .date() for i in self if i.is_working() ]

    def timenet_mean(self):
       return self.timenet() / self.working_days_number()

    def uptime_mean(self):
       return self.uptime() / self.working_days_number()

