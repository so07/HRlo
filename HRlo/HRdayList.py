#!/usr/bin/env python3
from datetime import timedelta, datetime

from .HRday import HRday
from .utils import to_str
from .logs.dayutils import day_range, week_bounds, month_weeks_bounds

class HRdayList(list):


    def __init__(self, label=None, **kwargs):

       self.hrday = HRday()

       self.label = label

       self.config = kwargs

       #self_hr_time = {}
       #self._hr_time['net'] = 0
       #for k in list(HRday.time_hash.keys()) + ['up']:
       #    self._hr_time[k] = timedelta(0)


    def __str__(self):
       s = ''

       if self.label:
          s += "."*25 + "{}\n".format(self.label)

       s += "{:.<25}".format("Working days")
       s += "{}\n".format( ", ".join([ str(i.day().date()) for i in self if i.working()]))
       s += "{:.<25}".format("Num. Working days")
       s += "{}\n".format( self.working() )
       #s += "{:.<25}".format("Working days list")
       #s += "{}\n".format( self.working(list=True) )
       s += "{:.<25}".format( "Uptime" )
       s += "{:<10}".format( to_str(self.hrday.uptime()) )
       s += " {} ".format( "for HR" )
       s += "{}\n".format( to_str(self.hrday['HR times']['up']) )
       s += "{:.<25}".format( "Timenet" )
       s += "{:<10}".format( to_str(self.timenet()) )
       s += " {} ".format( "for HR" )
       s += "{}\n".format( to_str(self.hrday['HR times']['net']) )
       s += "{:.<25}".format( "Time to work" )
       s += "{}\n".format( to_str(self.hrday.get('time_2work', 0)) )
       if self.hrday.get('time_2work'):
           s += "{:.<25}".format( "Worked time in %" )
           s += "{:.1f}%\n".format( 100.0*self.hrday.uptime().total_seconds()/self.hrday.get('time_2work', 1) )
       s += "{:.<25}".format( "Uptime mean" )
       s += "{}\n".format( to_str(self.mean(self.hrday.uptime())) )
       s += "{:.<25}".format( "Timenet mean" )
       s += "{}\n".format( to_str(self.mean(self.hrday.timenet())) )

       s += "{:.<25}".format("Timenets per day")
       s += "[{}]\n".format( ", ".join([ to_str(d.timenet()) for d in self if d.working()]) )

       if len(self.week_bounds()) > 1:
           s += "{:.<25}".format("Timenets per week")
           s += "[{}]\n".format( ", ".join([ to_str(d) for d in self.timenet_weeks() ]) )
           s += "{:.<25}".format("Working days per week")
           s += "{}\n".format( [ len([j for j in i if j]) for i in self._get_list_attr('working', weeks=True) ] )
           s += "{:.<25}".format("Week bounds")
           s += "[{}]\n".format(", ".join( [ "{}/{}".format(s, e) for s, e in self.week_bounds() ] ))

       if self.anomaly():
           s += "{:.<25}".format( "Anomaly" )
           s += "{}\n".format( self.anomaly() )

       s += "{:.<25}".format( "Lunch time" )
       s += "{}\n".format( to_str(self.hrday.get('time_lunch', timedelta(0))) )
       s += "{:.<25}".format( "Lunch time mean" )
       s += "{}\n".format( to_str(self.mean(self.hrday.get('time_lunch', timedelta(0)))) )

       return s


    def append(self, args):
       #if not args.working(): return
       list.append(self, args)

       self.hrday['uptime'] += args.uptime()

       for k in list(HRday.time_hash.keys()) + ['up', 'net']:
          self.hrday['HR times'][k] += args['HR times'][k]

       if not args.anomaly() and not args.holiday():
          self.hrday['timenet'] += args.timenet()

       for k in HRday.times_to_add:
           try:
               self.hrday[k] += args[k]
           except KeyError:
               self.hrday[k] = args[k]


    def __getitem__(self, index):
        if isinstance(index, int):
            return super(HRdayList, self).__getitem__(index)
        else:
            if isinstance(index, datetime):
                index = index.date()
            for d in self:
                if d['date'].date() == index:
                    return d
            raise IndexError("HRdayList index out of range")


    def week_bounds(self):
        _weeks = []
        if not self:
            return _weeks
        d = self[0]['date']
        while (d.date() < week_bounds(self[-1]['date'])[1]):
            _weeks.append(week_bounds(d))
            d += timedelta(days=7)
        return _weeks


    def days_per_week(self):
        _days_per_week = []
        for w in self.week_bounds():
            l = HRdayList()
            for d in day_range(w[0], w[1]):
                try:
                    l.append(self[d])
                except:
                    pass
            _days_per_week.append(l)
        return _days_per_week


    def _get_list_attr(self, attr, days=False, weeks=False):
        """Return list of values of attributes attr from HRday list."""
        if days:
            return [i for i in self if getattr(i, attr)()]
        elif weeks:
            return [ [getattr(d, attr)() for d in w] for w in self.days_per_week() ]
        else:
            return [getattr(i, attr)() for i in self]


    def report(self):
        return str(self)


    def uptime(self, list=False):
        """Return total uptime.
           If list=True return the list of all uptimes."""
        if list:
            return self._get_list_attr('uptime')
        else:
            up = timedelta(0)
            for i in self.uptime(list=True):
                up += i
            return up


    def anomaly(self, list=False):
        """Return number of anomalies.
           If list=True return the list of HRday with anomalies."""
        if list:
            return self._get_list_attr('anomaly', days=True)
        else:
            return len(self.anomaly(list=True))


    def working(self, list=False):
        """Return number of working days.
           If list=True return the list of working HRday."""
        if list:
            return self._get_list_attr('working', days=True)
        else:
            return len(self.working(list=True))


    def timenet(self, list=False):
        if list:
            return self._get_list_attr('timenet')
        else:
            tnet = sum(self.timenet(list=True))
            if self.config.get('overtime'):
                tnet -= timedelta(hours=self.config['overtime']).total_seconds()
            return tnet

    def timenet_weeks(self, list=False):
        if list:
            return self._get_list_attr('timenet', weeks=True)
        else:
            return  [ sum(w) for w in self.timenet_weeks(list=True) ]


    def mean(self, t):
        if self.working() == 0:
            if isinstance(t, timedelta):
                return timedelta(0)
            else:
                return 0
        return t / self.working(list=False)

