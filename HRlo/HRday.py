#!/usr/bin/env python3
import re
import sys
import datetime
import argparse

from HRlo.logs import dayutils

from HRlo.logs.daylog import DayLog

from . import HRauth
from . import HRget

class HRday(DayLog):

    re_logs = re.compile('(\d+)-')

    HR_workday      = datetime.timedelta(hours= 7, minutes=12)

    HR_login_last   = datetime.timedelta(hours=10, minutes= 0)

    # lunch timings
    HR_lunch_start = datetime.timedelta(hours=12, minutes= 0)
    HR_lunch_end   = datetime.timedelta(hours=15, minutes= 0)
    HR_lunch_time  = datetime.timedelta(hours=30, minutes= 0)

    sep_descr = '&&&'

    time_hash = {'ko'           : 'ORE KO', # NB: KO is time for lunch to subtract from uptime.
                 'rol'          : 'ROL',
                 'dayoff'       : 'FERIE',
                 'mission'      : 'MISSIONE',
                 'trip'         : 'TRASFERTA',
                 'bankhours'    : 'BANCA ORE GODUTA',
                 'bloodletting' : 'DONAZIONE SANGUE'}


    def __init__(self, field = None, data = None, label = None):

        self._now = datetime.datetime.today()
        self['label'] = label

        self._init_times()

        DayLog.__init__(self)

        if not field and not data:
           return

        self.HR = {k: v for k, v in zip(field, data)}

        # get date from HR
        date = datetime.datetime.strptime(self.HR['DATA'], "%Y-%m-%d")
        # get logs from TIMBRATURE of HR
        logs = self.re_logs.findall( self.HR['TIMBRATURE'] )

        # refine HR logs
        logs = [ i[0:2] + ':' + i[2:4] for i in logs ]

        # add now logs if today and odd logs
        if date.date() == self._now.date() and len(logs)%2:
            logs.append( self._now.strftime('%H:%M') )

        DayLog.__init__(self, date, logs)

        self['anomaly'] = int(self.HR['ANOMALIE'])

        self['timenet'] = self._get_timenet()

        # get working time to do for HR
        self['HR working time'] = self._get_hr_real_work_time()
        # get uptime/nettime for HR
        self['HR times']['up'], self['HR times']['net'] = self._get_hr_times()

        for k in ['ko', 'rol', 'trip', 'mission', 'dayoff', 'bloodletting']:
           self['HR times'][k] = self._get_hr_time(self.time_hash[k])


        # update uptime with mission/business trip times
        for k in ['trip', 'mission', 'bloodletting']:
           self['uptime'] += self['HR times'][k]

        sep = self.sep_descr
        # read from DESCRIZIONE1 field
        for k, v in zip(self.HR['DESCRIZIONE1'].split(sep), self.HR['QTA1'].split(sep)):

            # from ORE
            if 'ORE' in k:
               if 'ECCEDENTI' in k:
                  #self._hr_time_net += self._unit_hr2seconds( float(v) )
                  pass
               if 'MANCANTI' in k:
                  #self._hr_time_net -= self._unit_hr2seconds( float(v) )
                  pass

            # from IND.
            if 'IND' in k:
               if 'MENSA' in k:
                  self['lunch'] = int(float(v))
               if 'DI MISSIONE' in k:
                  self['mission'] = int(float(v))


    def __str__ (self):
       s = ''
       if not self.date():
           return s
       #s += DayLog.__str__(self) + '\n'

       if self['label']:
          s += "."*20 + "{}\n".format(self['label'])

       # date
       s += "{:.<20}".format( "Date" )
       s += "{}\n".format( str(self.date().date()) )

       # uptime
       s += "{:.<20}".format( "Uptime" )
       s += "{:<10}".format( dayutils.sec2str(self.uptime().total_seconds()) )
       if not self.is_today():
          s += " {} ".format( "for HR" )
          s += "{}".format( dayutils.sec2str(self['HR times']['up'].total_seconds()) )
       s += '\n'

       # timenet
       s += "{:.<20}".format( "Timenet" )
       s += "{:<10}".format( dayutils.sec2str(self.timenet()) )
       if not self.is_today():
          s += " {} ".format( "for HR" )
          s += "{}".format( dayutils.sec2str(self['HR times']['net']) )
       s += '\n'

       s += "{:.<20}".format( "Lunch" )
       s += "{}\n".format( self['lunch'] )
       # KO time
       if self['HR times']['ko']:
          s += "{:.<20}".format( "KO time" )
          s += "{}\n".format( self['HR times']['ko'] )

       # ROL time
       if self['HR times']['rol']:
          s += "{:.<20}".format( "ROL time" )
          s += "{}\n".format( self['HR times']['rol'] )

       # DAYOFF time
       if self['HR times']['dayoff']:
          s += "{:.<20}".format( "DayOff time" )
          s += "{}\n".format( self['HR times']['rol'] )

       # TRIP time
       if self['HR times']['trip']:
          s += "{:.<20}".format( "Business trip time" )
          s += "{}\n".format( self['HR times']['trip'] )

       # MISSION time
       if self['HR times']['mission']:
          s += "{:.<20}".format( "Mission time" )
          s += "{}\n".format( self['HR times']['mission'] )

       if self.is_mission():
          s += "{:.<20}".format( "Mission" )
          s += "{}\n".format( self['mission'] )

       if self.logs():
          s += "{:.<20}".format( "TimeStamps" )
          s += "[{}]\n".format( ", ".join([ i.time().strftime("%H:%M") for i in self.logs()]) )

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


    def __repr__(self):
       return str(self.date().date())


    def __add__(self, other):

       a = HRday()

       sum_daylog = DayLog.__add__(self, other)

       a['logs']   = sum_daylog.logs()
       a['date']   = sum_daylog.date()
       a['uptime'] = sum_daylog.uptime()

       a['timenet'] = self.timenet() + other.timenet()
       a['anomaly'] = self.anomaly() + other.anomaly()

       a['HR working time'] = self['HR working time'] + other['HR working time']
       a['lunch'] = self['lunch'] + other['lunch']
       a['mission'] = self['mission'] + other['mission']

       for k in self['HR times'].keys():
          a['HR times'][k] = self['HR times'][k] + other['HR times'][k]

       return a


    def _init_times (self):

        self['timenet'] = 0
        self['anomaly'] = 0

        self['HR working time'] = 0
        self['lunch'] = 0
        self['mission'] = 0

        self['HR times'] = {}

        self['HR times']['net'] = 0
        for k in list(self.time_hash.keys()) + ['up']:
           self['HR times'][k] = datetime.timedelta(0)


    def _unit_hr2seconds(self, hrtime):
        # convert to second
        return float(hrtime) *60.0*60.0

    def _unit_hr2timedelta(self, hrtime):
        return datetime.timedelta(seconds=self._unit_hr2seconds(hrtime))

    def _is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False


    def _get_timenet(self):

       # CHANGEIT
       d = self.date().weekday()
       if d == 5 or d == 6:
          return 0

       exc = self.uptime() - self.HR_workday

       # times to subtract
       for k in ['ko']:
          exc -= self._get_hr_time(self.time_hash[k])

       # times to add
       for k in ['rol', 'trip', 'mission', 'dayoff', 'bankhours', 'bloodletting']:
          exc += self._get_hr_time(self.time_hash[k])

       # convert in seconds
       exc_sec = exc.total_seconds()

       return exc_sec


    def _check_hr_work_time(self, type_, time_):
        """Check HR work time in DESCRORARIO key."""

        if self.HR['DESCRORARIO'].strip() == 'NON IN FORZA':
            print("[HRday] ***ERROR***")
            print("Worker not employed in date", self.date().date())
            sys.exit(-1)

        if not self._is_number(time_[0]) or not self._is_number(time_[1]):
            print("[HRday] ***ERROR***")
            print("HR Time not well defined on date", self.date().date())
            #print(type_, time_)
            sys.exit(-1)


    def _get_hr_work_time(self):
       """Return working time for HR in seconds.
          Get data from DESCRORARIO key.
          If day is holiday return 0.
       """
       # read from DESCRORARIO to get working time for HR
       if self.is_holiday():
          _time_sec = 0
       else:
          _time_info = self.HR['DESCRORARIO'].split()
          _time_type = _time_info[0]
          _time_time = _time_info[1].split(':')
          self._check_hr_work_time(_time_type, _time_time)
          _time_delta = datetime.timedelta( hours=int(_time_time[0]), minutes=int(_time_time[1]) )
          # convert to seconds
          _time_sec  = _time_delta.total_seconds()
       #print(self.HR['DESCRORARIO'], _time_sec)
       return _time_sec


    def _get_hr_real_work_time(self):
       """Return real working time for HR in seconds involving rol, dayoff time.
          If day is holiday return 0.
       """
       _hr_work_time_sec = self._get_hr_work_time()
       _hr_work_time = datetime.timedelta( seconds=_hr_work_time_sec )

       # times to subtract
       for k in ['rol', 'dayoff', 'bankhours', 'bloodletting']:
          _hr_work_time -= self._get_hr_time(self.time_hash[k])

       _time_sec  = _hr_work_time.total_seconds()

       return _time_sec


    def _get_hr_times(self):
       _oreord = self.HR['OREORD']
       _oreecc = self.HR['OREECC']
       #print (_oreord, _oreecc)

       _oreord_sec = self._unit_hr2seconds(_oreord)
       _oreecc_sec = self._unit_hr2seconds(_oreecc)
       _oretot_sec = _oreord_sec + _oreecc_sec

       _uptime  = datetime.timedelta( seconds=_oretot_sec )
       _timenet = _oretot_sec - self['HR working time']
       return _uptime, _timenet


    def _get_hr_time(self, key):
        """Return KEY time in datetime.timedelta.
           Get data from KEY flag in DESCRIZIONE1 field.
           Return time in datetime.timedelta.
        """
        sep = self.sep_descr
        for k, v in zip(self.HR['DESCRIZIONE1'].split(sep), self.HR['QTA1'].split(sep)):
           if k.startswith(key):
           #if key in k:
               return self._unit_hr2timedelta(v)
        return datetime.timedelta(0)


    def anomaly(self):
        return self['anomaly']


    def timenet(self):
       return self['timenet']


    def remains(self, fmt = None):
        if not self.is_today():
           return None
        r = self.HR_workday - self.uptime()
        if r.total_seconds() < 0:
           return datetime.timedelta(0)
        else:
           return r


    def exit(self, fmt = None):
        if not self.is_today():
           return None
        return  (self._now + self.remains()).time()


    def is_holiday(self):
       """Return True if day is an holiday otherwise return False.
          Check if DESCRORARIO key is equal to SABATO, DOMENICA, FESTIVO.
       """
       _desc = self.HR['DESCRORARIO'].split()[0]
       _holiday = ['SABATO', 'DOMENICA', 'FESTIVO']
       #if [s for s in _holiday if _desc in s]:
       if any(_desc in s for s in _holiday):
           return True
       else:
           return False


    def is_working(self):
       if not self.logs() and not self.is_mission() and self.is_holiday():
          return False
       # check for holiday
       if self.is_holiday():
           return False
       # check for dayoff
       if self.is_dayoff():
           return False
       # check for total rol day
       if self.is_rol_total():
          return False
       # check for bloodletting
       if self.is_bloodletting():
           return False
       return True


    def is_mission(self):
       if self.get('mission'):
       #if hasattr(self, '_mission') and self._mission:
           return True
       else:
           return False


    def is_transfer(self):
       return self._get_hr_time(self.time_hash['trip'])


    def is_dayoff(self):
        """Check for dayoff.
           Return total dayoff time in datetime.timedelta.
        """
        return self._get_hr_time(self.time_hash['dayoff'])


    def is_rol(self):
        """Check for ROL time.
           Return total ROL time in datetime.timedelta.
        """
        return self._get_hr_time(self.time_hash['rol'])


    def is_rol_total(self):
        """Check for entire day ROL.
           Return bool.
           If holiday return False.
        """

        if self.is_holiday():
            return False

        _rol_seconds = self._get_hr_time(self.time_hash['rol']).total_seconds()
        if _rol_seconds == self._get_hr_work_time():
           return True
        else:
           return False


    def is_bankhours(self):
       return self._get_hr_time(self.time_hash['bankhours'])


    def is_bloodletting(self):
       return self._get_hr_time(self.time_hash['bloodletting'])


    def is_today(self):
       if self.date().date() == self._now.date():
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

    parser = argparse.ArgumentParser(prog='HRday',
                                     description='',
                                     formatter_class=argparse.RawTextHelpFormatter)


    HRget.add_parser(parser)

    HRauth.add_parser(parser)

    args = parser.parse_args()


    auth = HRauth.HRauth(**vars(args))

    h = HRget.HRget(auth, verbose=False)

    json = h.get(year=args.year, month=args.month, day=args.day)

    f, d = json['Fields'], json['Data']

    #for i, j in zip(f, d):
    #    print(i, j)
    #print(d)

    day = HRday( f, d )
    print(day)


if __name__ == '__main__':
    #debug()
    main()
