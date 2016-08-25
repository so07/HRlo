#!/usr/bin/env python3
import datetime

from .logs.dayutils import dayutils

from . import HRday

class HRdayList(list):

    def __init__(self, label=None):

       self.hrday = HRday.HRday()

       #self_hr_time = {}
       #self._hr_time['net'] = 0
       #for k in list(HRday.HRday.time_hash.keys()) + ['up']:
       #    self._hr_time[k] = datetime.timedelta(0)

       self.label = label


    def __str__(self):
       s = ''

       if self.label:
          s += "."*25 + "{}\n".format(self.label)

       s += "{:.<25}".format("Working days")
       s += "{}\n".format( ", ".join([ str(i.day().date()) for i in self if i.is_working()]))
       s += "{:.<25}".format("Num. Working days")
       s += "{}\n".format( self.working_days_number() )
       #s += "{:.<25}".format("Working days list")
       #s += "{}\n".format( self.working_days_list() )
       s += "{:.<25}".format( "Uptime" )
       s += "{:<10}".format( dayutils.sec2str(self.hrday.uptime().total_seconds()) )
       s += " {} ".format( "for HR" )
       s += "{}\n".format( dayutils.sec2str(self.hrday['HR times']['up'].total_seconds()) )
       s += "{:.<25}".format( "Timenet" )
       s += "{:<10}".format( dayutils.sec2str(self.hrday.timenet()) )
       s += " {} ".format( "for HR" )
       s += "{}\n".format( dayutils.sec2str(self.hrday['HR times']['net']) )
       s += "{:.<25}".format( "Time to work" )
       s += "{}\n".format( dayutils.sec2str(self.hrday.get('time_2work', 0)) )
       s += "{:.<25}".format( "Uptime mean" )
       s += "{}\n".format( dayutils.sec2str(self.mean(self.hrday.uptime().total_seconds())) )
       s += "{:.<25}".format( "Timenet mean" )
       s += "{}\n".format( dayutils.sec2str(self.mean(self.hrday.timenet())) )
       #s += "{:.<25}".format("Logs")
       #for j in self:
       #   s += "[{}] ".format(", ".join([ i.time().strftime(dayutils.fmt_time) for i in j.logs() ]))
       #s += '\n'

       s += "{:.<25}".format("Timenets")
       s += "[{}]\n".format( ", ".join([ dayutils.sec2str(d.timenet()) for d in self if d.is_working()]) )

       if self.anomaly():
           s += "{:.<25}".format( "Anomaly" )
           s += "{}\n".format( self.anomaly() )

       s += "{:.<25}".format( "Lunch time" )
       s += "{}\n".format( dayutils.sec2str(self.hrday.get('time_lunch', datetime.timedelta(0)).total_seconds()) )
       s += "{:.<25}".format( "Lunch time mean" )
       s += "{}\n".format( dayutils.sec2str(self.mean(self.hrday.get('time_lunch', datetime.timedelta(0)).total_seconds())) )

       return s

    def append(self, args):
       #if not args.is_working(): return
       list.append(self, args)

       self.hrday['uptime'] += args.uptime()

       for k in list(HRday.HRday.time_hash.keys()) + ['up', 'net']:
          self.hrday['HR times'][k] += args['HR times'][k]

       if not args.anomaly() and not args.is_holiday():
          self.hrday['timenet'] += args.timenet()

       for k in HRday.HRday.times_to_add:
           try:
               self.hrday[k] += args[k]
           except KeyError:
               self.hrday[k] = args[k]


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
       return [ i.date() for i in self if i.is_working() ]

    def mean(self, t):
        if self.working_days_number() == 0:
            if isinstance(t, datetime.timedelta):
                return datetime.timedelta(0)
            else:
                return 0
        return t / self.working_days_number()

