#!/usr/bin/env python3
import re
import sys
import datetime

from logs import dayutils

from logs.daylog import DayLog

class HRday(DayLog):

    re_logs = re.compile('(\d+)-')

    HR_workday      = datetime.timedelta(hours= 7, minutes=12)

    HR_login_last   = datetime.timedelta(hours=10, minutes= 0)

    # lunch timings
    HR_lunch_start = datetime.timedelta(hours=12, minutes= 0)
    HR_lunch_end   = datetime.timedelta(hours=15, minutes= 0)
    HR_lunch_time  = datetime.timedelta(hours=30, minutes= 0)

    def __init__(self, field = None, data = None, label = None):

        self._now = datetime.datetime.today()
        self.label = label

        self._timenet = 0
        self._anomaly = 0

        self._hr_working_time = 0
        self._lunch = 0
        self._mission = 0

        self._hr_uptime = datetime.timedelta(0)
        self._hr_timenet = 0

        DayLog.__init__(self)

        if not field and not data:
           return

        self.HR = {k: v for k, v in zip(field, data)}

        date = datetime.datetime.strptime(self.HR['DATA'], "%Y-%m-%d")
        logs = self.re_logs.findall( self.HR['TIMBRATURE'] )

        logs = [ i[0:2] + ':' + i[2:4] for i in logs ]

        if date.date() == self._now.date() and len(logs)%2:
            logs.append( self._now.strftime('%H:%M') )

        DayLog.__init__(self, date, logs)

        self._anomaly = int(self.HR['ANOMALIE'])

        self._timenet = self._get_timenet()

        #

        self._hr_working_time = self._get_hr_working_time()
        self._hr_uptime, self._hr_timenet = self._get_hr_times()

        sep = '&&&'
        # read from DESCRIZIONE1 field
        for k, v in zip(self.HR['DESCRIZIONE1'].split(sep), self.HR['QTA1'].split(sep)):

            # from ORE
            if 'ORE' in k:
               if 'ECCEDENTI' in k:
                  #self._hr_timenet += self._unit_hr2seconds( float(v) )
                  pass
               if 'MANCANTI' in k:
                  #self._hr_timenet -= self._unit_hr2seconds( float(v) )
                  pass
               if 'KO' in k:
                  # time for lunch (to subtract from uptime)
                  pass

            # from IND.
            if 'IND' in k:
               if 'MENSA' in k:
                  self._lunch = int(float(v))
               if 'DI MISSIONE' in k:
                  self._mission = int(float(v))

            # from MISSION (not with IND.)
            if 'MISSIONE' in k and not 'IND' in k:
               pass

        # update for mission
        pass


    def __str__ (self):
       s = ''
       if not self._date or not self.is_working():
           return s
       #s += DayLog.__str__(self) + '\n'

       if self.label:
          s += "."*20 + "{}\n".format(self.label)

       s += "{:.<20}".format( "Date" )
       s += "{}\n".format( str(self._date.date()) )
       s += "{:.<20}".format( "Uptime" )
       s += "{:<10}".format( dayutils.sec2str(self._uptime.total_seconds()) )
       s += " {} ".format( "for HR" )
       s += "{}\n".format( dayutils.sec2str(self._hr_uptime.total_seconds()) )
       s += "{:.<20}".format( "Timenet" )
       s += "{:<10}".format( dayutils.sec2str(self.timenet()) )
       s += " {} ".format( "for HR" )
       s += "{}\n".format( dayutils.sec2str(self._hr_timenet) )
       s += "{:.<20}".format( "Lunch" )
       s += "{}\n".format( self._lunch )
       if self._logs:
          s += "{:.<20}".format( "TimeStamps" )
          s += "[{}]\n".format( ", ".join([ i.time().strftime("%H:%M") for i in self._logs]) )
       if self.is_mission():
          s += "{:.<20}".format( "Mission" )
          s += "{}\n".format( self._mission )
       s += "{:.<20}".format( "Anomaly" )
       s += "{}\n".format( str(self.anomaly()) )

       #if not self.is_working():
       #   return s
       if self.is_today():
          s += "{:.<20}".format( "Remains" )
          s += "{}\n".format( str(self.remains()) )
          s += "{:.<20}".format( "Estimated exit" )
          s += "{}\n".format( str(self.exit().strftime("%H:%M")) )

       return s

    def _unit_hr2seconds(self, hrtime):
        # convert to second
        return hrtime *60.0*60.0
    def _unit_hr2timedelta(self, hrtime):
        return datetime.timedelta(seconds=self._unit_hr2seconds(hrtime))

    def __repr__(self):
       return str(self._date.date())

    def __add__(self, other):

       a = HRday()

       sum_daylog = DayLog.__add__(self, other)

       a._logs = sum_daylog._logs
       a._date = sum_daylog._date
       a._uptime = sum_daylog._uptime

       a._timenet = self._timenet + other._timenet
       a._anomaly = self._anomaly + other._anomaly

       #

       a._hr_working_time = self._hr_working_time + other._hr_working_time
       a._lunch = self._lunch + other._lunch
       a._mission = self._mission + other._mission
       a._hr_uptime = self._hr_uptime + other._hr_uptime
       a._hr_timenet = self._hr_timenet + other._hr_timenet

       return a


    def anomaly(self):
        return self._anomaly

    def timenet(self):
       return self._timenet

    def remains(self, fmt = None):
        if not self.is_today():
           return None
        r = self.HR_workday - self._uptime
        if r.total_seconds() < 0:
           return datetime.timedelta(0)
        else:
           return r

    def exit(self, fmt = None):
        if not self.is_today():
           return None
        return  (self._now + self.remains()).time()

    def _get_timenet(self):

       d = self._date.weekday()
       if d == 5 or d == 6:
          return 0

       exc = self._uptime - self.HR_workday
       exc_sec = exc.total_seconds()
       return exc_sec

    def _get_hr_working_time(self):
       # read from DESCRORARIO to get working time for HR
       _time_info = self.HR['DESCRORARIO'].split()
       if 'SABATO' in _time_info or 'DOMENICA' in _time_info:
          _time_sec = 0
       else:
          _time_type = _time_info[0]
          _time_time = _time_info[1].split(':')
          _time_sec  = datetime.timedelta( hours=int(_time_time[0]), minutes=int(_time_time[1]) ).total_seconds()
       #print(_time_sec)
       return _time_sec

    def _get_hr_times(self):
       _oreord = float(self.HR['OREORD'])
       _oreecc = float(self.HR['OREECC'])
       #print (_oreord, _oreecc)

       _oreord_sec = self._unit_hr2seconds(_oreord)
       _oreecc_sec = self._unit_hr2seconds(_oreecc)
       _oretot_sec = _oreord_sec + _oreecc_sec

       _uptime  = datetime.timedelta( seconds=_oretot_sec )
       _timenet = _oretot_sec-self._hr_working_time
       return _uptime, _timenet


    def is_working(self):
       if not self.logs() and not self.is_mission():
          return False
       else:
          return True

    def is_mission(self):
       if hasattr(self, '_mission') and self._mission:
           return True
       else:
           return False

    def is_today(self):
       if self._date.date() == self._now.date():
          return True
       else:
          return False


def debug():

    f = []
    d = []
    with open('file', 'r') as fp:
       for line in fp:
          lf, ld = line.strip().split('=')
          print( lf, ld )
          f.append(lf.strip(' '))
          d.append(ld.strip(' '))
    #print(data)
    day = HRday(f, d)

    print(day)
    #sys.exit()



def main():

    import argparse
    import HRget, HRauth

    parser = argparse.ArgumentParser(prog='HRday',
                                     description='',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    HRget.add_parser(parser)

    HRauth.add_parser(parser)

    args = parser.parse_args()


    auth = HRauth.HRauth(**vars(args))

    h = HRget.HRget(auth, verbose=False)

    f, d = h.get(year=args.year, month=args.month, day=args.day)

    #for i, j in zip(f, d):
    #    print(i, j)
    #print(d)

    day = HRday( f, d )
    print(day)


if __name__ == '__main__':
    #debug()
    main()
