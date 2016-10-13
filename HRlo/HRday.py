#!/usr/bin/env python3
import re
import datetime
import argparse

from .logs import dayutils

from .logs.daylog import DayLog

from . import HRauth
from . import HRget

from . import utils

class HRday(DayLog):

    re_logs = re.compile('(\d+)-')

    HR_workday                  = datetime.timedelta(hours= 7, minutes=12)
    HR_workday_least            = datetime.timedelta(hours= 5, minutes= 0)
    HR_workday_least_with_lunch = datetime.timedelta(hours= 6, minutes= 0)

    HR_login_last   = datetime.timedelta(hours=10, minutes= 0)

    # lunch timings
    HR_lunch_start = datetime.time(hour=12, minute= 0)
    HR_lunch_end   = datetime.time(hour=15, minute= 0)
    HR_lunch_time  = datetime.timedelta(hours=0, minutes=30)


    sep_descr = '&&&'

    time_hash = {
        'ko'                                 : 'ORE KO', # NB: KO is time for lunch to subtract from uptime.
        'rol'                                : 'ROL',
        'dayoff'                             : 'FERIE',
        'mission'                            : 'MISSIONE',
        'trip'                               : 'TRASFERTA',
        'bankhours'                          : 'BANCA ORE GODUTA',
        'marital leave'                      : 'CONGEDO MATRIMONIALE',
        'father discharge'                   : 'CONGEDO OBBLIGATORIO PADRE',
        'marrowletting'                      : 'DONAZIONE MIDOLLO',
        'bloodletting'                       : 'DONAZIONE SANGUE',
        'disease'                            : 'MALATTIA',
        'disease_company'                    : 'MALATTIA CARICO AZIENDA',
        'baby disease > 3 yrs'               : 'MALATTIA BAMBINO > 3',
        'baby disease <= 3 yrs'              : 'MALATTIA BAMBINO <= 3 ANNI',
        'optional maternity leave'           : 'MATERN./PATERN. FACOLT. (0 - 6 ANNI)',
        'optional maternity leave not paied' : 'MAT./PAT. FACOLT. NON RETR (7 - 12 ANNI)',
        'relative bereavement'               : 'PERMESSO LUTTO AFFINI',
        'bereavement'                        : 'PERMESSO LUTTO E GRAVI MOTIVI',
        'strike'                             : 'SCIOPERO',
    }

    sub_times_to_timenet = ['ko', 'bankhours']
    add_times_to_timenet = ['rol', 'dayoff', 'mission', 'trip', 'bankhours',
                            'marital leave', 'father discharge', 'marrowletting', 'bloodletting',
                            'disease', 'baby disease > 3 yrs', 'baby disease <= 3 yrs',
                            'optional maternity leave', 'optional maternity leave not paied',
                            'relative bereavement', 'bereavement', 'strike']

    sub_times_to_hr = ['rol', 'dayoff',
                       'marital leave', 'father discharge', 'marrowletting', 'bloodletting',
                       'disease', 'baby disease > 3 yrs', 'baby disease <= 3 yrs',
                       'optional maternity leave', 'optional maternity leave not paied',
                       'relative bereavement', 'bereavement', 'strike']

    time_for_is_working = ['dayoff',
                           'marital leave', 'father discharge', 'marrowletting', 'bloodletting',
                           'disease', 'disease_company', 'baby disease > 3 yrs', 'baby disease <= 3 yrs',
                           'bloodletting', 'marrowletting',
                           'optional maternity leave', 'optional maternity leave not paied',
                           'relative bereavement', 'bereavement', 'strike']

    times_to_add = ['time_lunch', 'time_ko', 'time_2work', 'lunch', 'anomaly', 'mission']

    def __init__(self, json=None, label=None):

        self._now = datetime.datetime.today()
        self['label'] = label

        self._init_times()

        DayLog.__init__(self)

        if not json:
           return

        self.HR = {k: v for k, v in zip(json['Fields'], json['Data'])}

        # get data from HR ...

        # get number of anomalies from HR
        self['anomaly'] = int(self.HR['ANOMALIE'])
        # get working time to do for HR
        self['HR working time'] = self._get_hr_real_work_time()
        # get uptime/nettime for HR
        self['HR times']['up'], self['HR times']['net'] = self._get_hr_times()
        # get lunch benefits
        self['lunch'] = self.lunch()
        # get mission benefits
        self['mission'] = self.mission()
        # get HR times
        for k in self.time_hash.keys():
           self['HR times'][k] = self._get_hr_time(self.time_hash[k])

        # ... end get data from HR


        # init data for Daylog ...

        # get date from HR
        date = datetime.datetime.strptime(self.HR['DATA'], "%Y-%m-%d")
        # get logs from TIMBRATURE of HR
        logs = self.re_logs.findall( self.HR['TIMBRATURE'] )

        # refine HR logs
        logs = [ i[0:2] + ':' + i[2:4] for i in logs ]

        # add now logs if today and odd logs
        if date.date() == self._now.date() and len(logs)%2:
            logs.append( self._now.strftime('%H:%M') )

        # init DayLog class
        DayLog.__init__(self, date, logs)

        # ... end init data for DayLog

        self['time_lunch'] = self._get_lunch_time()
        self['time_ko'] = self._get_ko_time()
        self['time_2work'] = self._get_hr_real_work_time()

        # add timenet key to Daylog class
        self['timenet'] = self._get_timenet()

        # update uptime with mission/business trip times
        for k in ['trip', 'mission', 'bloodletting']:
           self['uptime'] += self['HR times'][k]


# __str__ {{{

    def __str__ (self):
       s = ''
       if not self.date():
           return s
       #s += DayLog.__str__(self) + '\n'

       if self['label']:
          s += "."*25 + "{}\n".format(self['label'])

       # date
       s += "{:.<25}".format( "Date" )
       s += "{}\n".format( str(self.date().date()) )

       # not working day
       if not self.working():
           s += "{:.<25}".format( "Working day" )
           s += "{}\n".format( self.working() )

       # uptime
       s += "{:.<25}".format( "Uptime" )
       s += "{:<10}".format( utils.to_str(self.uptime()) )
       if not self.is_today():
          s += " {} ".format( "for HR" )
          s += "{}".format( utils.to_str(self['HR times']['up']) )
       s += '\n'

       # timenet
       s += "{:.<25}".format( "Timenet" )
       s += "{:<10}".format( utils.to_str(self.timenet()) )
       if not self.is_today():
          s += " {} ".format( "for HR" )
          s += "{}".format( utils.to_str(self['HR times']['net']) )
       s += '\n'

       # time to work
       s += "{:.<25}".format( "Time to work" )
       s += "{:<10}".format( utils.to_str(self.time_to_work()) )
       s += '\n'

       if self.time_to_work():
           # percentage of worked time
           s += "{:.<25}".format( "Worked time in %" )
           s += "{:.1f}%".format( 100.0*self.uptime().total_seconds()/self.time_to_work() )
           s += '\n'

       if not self.is_today():
          s += "{:.<25}".format( "Lunch" )
          s += "{}\n".format( self['lunch'] )
       # lunch time
       s += "{:.<25}".format( "Lunch time" )
       s += "{}".format( utils.to_str(self['time_lunch']) )
       s += '\n'

       # KO time
       if self['HR times']['ko']:
          s += "{:.<25}".format( "KO time" )
          s += "{}\n".format( utils.to_str(self['HR times']['ko']) )
       if self['time_ko'] and not self['HR times']['ko'] and self.working():
          s += "{:.<25}".format( "KO time" )
          s += "{}\n".format( utils.to_str(self['time_ko']) )

       # ROL time
       if self['HR times']['rol']:
          s += "{:.<25}".format( "ROL time" )
          s += "{}\n".format( self['HR times']['rol'] )

       # DAYOFF time
       if self['HR times']['dayoff']:
          s += "{:.<25}".format( "DayOff time" )
          s += "{}\n".format( self['HR times']['rol'] )

       # TRIP time
       if self['HR times']['trip']:
          s += "{:.<25}".format( "Business trip time" )
          s += "{}\n".format( self['HR times']['trip'] )

       # MISSION time
       if self['HR times']['mission']:
          s += "{:.<25}".format( "Mission time" )
          s += "{}\n".format( self['HR times']['mission'] )

       if self.mission():
          s += "{:.<25}".format( "Mission" )
          s += "{}\n".format( self['mission'] )

       if self.logs():
          s += "{:.<25}".format( "TimeStamps" )
          s += "[{}]\n".format( ", ".join([ i.time().strftime("%H:%M") for i in self.logs()]) )

       if self.anomaly():
          s += "{:.<25}".format( "Anomaly" )
          s += "{}\n".format( str(self.anomaly()) )

       #if not self.working():
       #   return s
       if self.is_today():
          s += "{:-<25}\n".format( "---- Estimated Exits " )
          # with lunch
          s += "{:.<25}{}\n".format( "Standard time", utils.to_str(self.HR_workday) )
          s += "{:.<25}".format( "Remains" )
          s += "{}\n".format( utils.to_str(self.remains(lunch=True, least=False)) )
          s += "{:.<25}".format( "Estimated exit" )
          s += "{}\n".format( str(self.exit(lunch=True, least=False).strftime("%H:%M")) )
          # at least with lunch
          s += "{:.<25}{}\n".format( "At least with lunch time", utils.to_str(self.HR_workday_least_with_lunch) )
          s += "{:.<25}".format( "Remains" )
          s += "{}\n".format( utils.to_str(self.remains(lunch=True, least=True)) )
          s += "{:.<25}".format( "Estimated exit" )
          s += "{}\n".format( str(self.exit(lunch=True, least=True).strftime("%H:%M")) )
          # at least
          s += "{:.<25}{}\n".format( "At least working time", utils.to_str(self.HR_workday_least) )
          s += "{:.<25}".format( "Remains" )
          s += "{}\n".format( utils.to_str(self.remains(lunch=False, least=True)) )
          s += "{:.<25}".format( "Estimated exit" )
          s += "{}\n".format( str(self.exit(lunch=False, least=True).strftime("%H:%M")) )
       return s

# }}}

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

       for k in self.times_to_add:
           a[k] = self[k] + other[k]

       return a


    def _init_times (self):
        """Inititalize times."""

        self['timenet'] = 0
        self['anomaly'] = 0

        self['HR working time'] = 0
        self['lunch'] = 0
        self['mission'] = 0

        self['HR times'] = {}

        self['HR times']['net'] = 0
        for k in list(self.time_hash.keys()) + ['up']:
           self['HR times'][k] = datetime.timedelta(0)


    def _get_timenet(self):
       """Return timenet in seconds."""

       if self.holiday():
          return 0

       time = self.uptime()

       # times to subtract
       for k in self.sub_times_to_timenet:
          time -= self._get_hr_time(self.time_hash[k])

       if self.get('time_ko') and self.is_today():
           time -= self['time_ko']

       # times to add
       for k in self.add_times_to_timenet:
          time += self._get_hr_time(self.time_hash[k])

       # subtract HR work day
       time -= self.HR_workday

       # convert in seconds
       time_sec = time.total_seconds()

       return time_sec


    def _check_hr_work_time(self, type_, time_):
        """Check HR work time in DESCRORARIO key."""

        if self.HR['DESCRORARIO'].strip() == 'NON IN FORZA':
            raise Exception("[HRday] ***ERROR***\nWorker not employed in date {}".format(self.date().date()))

        if not utils.is_number(time_[0]) or not utils.is_number(time_[1]):
            raise Exception("[HRday] ***ERROR***\nHR Time not well defined on date {}".format(self.date().date()))


    def _get_hr_work_time(self):
       """Return working time for HR in seconds.
          Get data from DESCRORARIO key.
          If day is holiday return 0.
       """
       # read from DESCRORARIO to get working time for HR
       if self.holiday():
          _time_sec = 0
       else:
          _time_info = self.HR['DESCRORARIO'].split()
          _time_type = _time_info[0]
          _time_time = _time_info[1].split(':')
          self._check_hr_work_time(_time_type, _time_time)
          _time_delta = datetime.timedelta( hours=int(_time_time[0]), minutes=int(_time_time[1]) )
          # convert to seconds
          _time_sec  = _time_delta.total_seconds()
       return _time_sec


    def _get_hr_real_work_time(self):
       """Return real working time for HR in seconds involving all hashed times (see time_hash list).
          If day is holiday return 0.
       """
       _hr_work_time_sec = self._get_hr_work_time()
       _hr_work_time     = datetime.timedelta( seconds=_hr_work_time_sec )

       # times to subtract
       for k in self.sub_times_to_hr:
          _hr_work_time -= self._get_hr_time(self.time_hash[k])

       _time_sec  = _hr_work_time.total_seconds()

       return _time_sec


    def _get_hr_times(self):
       _oreord = self.HR['OREORD']
       _oreecc = self.HR['OREECC']

       _oreord_sec = utils.hr2seconds(_oreord)
       _oreecc_sec = utils.hr2seconds(_oreecc)
       _oretot_sec = _oreord_sec + _oreecc_sec

       _uptime  = datetime.timedelta( seconds=_oretot_sec )
       _timenet = _oretot_sec - self['HR working time']
       return _uptime, _timenet


    def _get_hr_data_from_description (self, key):
        """Return VALUE of KEY in DESCRIZIONE1 field of HR data."""
        sep = self.sep_descr
        for k, v in zip(self.HR['DESCRIZIONE1'].split(sep), self.HR['QTA1'].split(sep)):
            if k.startswith(key):
            #if key in k:
               return v


    def _get_hr_time(self, key):
        """Return KEY time in datetime.timedelta.
           Get data from KEY flag in DESCRIZIONE1 field.
           Return time in datetime.timedelta.
        """
        value = self._get_hr_data_from_description(key)
        if value:
            return utils.hr2time(value)
        else:
            return datetime.timedelta(0)


    def _get_lunch_time(self):
        """Return lunch time between lunch start and end times.
           Return time in datetime.timedelta.
        """
        lunch_start = datetime.datetime.combine( self.date(), self.HR_lunch_start )
        lunch_end   = datetime.datetime.combine( self.date(), self.HR_lunch_end )
        working_time_during_lunch_time = self.uptime( lunch_start, lunch_end )
        if not working_time_during_lunch_time:
            return datetime.timedelta(0)
        # last time
        time_final = lunch_end
        if self._now < lunch_end:
            time_final = self._now
        # start time
        time_start = lunch_start
        if self._now < time_start:
            return datetime.timedelta(0)
        # get lunch time
        time_lunch = time_final - time_start - self.uptime( lunch_start, lunch_end )
        return time_lunch


    def _get_ko_time(self):
        """Return ko time.
           Return time in datetime.timedelta.
        """
        _time_ko = self.HR_lunch_time - self['time_lunch']
        if _time_ko < datetime.timedelta(0):
           _time_ko = datetime.timedelta(0)
        return _time_ko


    def _get_lunch_time_remain(self):
        """Return remaining time to reach HR launch time.
           Return time in datetime.timedelta.
        """
        _lunch_time = self._get_lunch_time()
        if _lunch_time > self.HR_lunch_time:
            return datetime.timedelta(0)
        else:
            return self.HR_lunch_time -_lunch_time


    def report(self):
        return str(self)


    def anomaly(self):
        """Return number of anomalies found."""
        return self['anomaly']


    def timenet(self):
        """Return timenet in seconds."""
        return self['timenet']


    def time_to_work(self):
        """Return working time in seconds."""
        return self._get_hr_work_time()


    def remains(self, lunch=True, least=False):
        if not self.is_today():
           return None

        time_to_work = self.HR_workday + self._get_lunch_time_remain()

        if least and not lunch:
            time_to_work = self.HR_workday_least

        if least and lunch:
            time_to_work = self.HR_workday_least_with_lunch

        r = time_to_work - self.uptime()

        if r.total_seconds() < 0:
           return datetime.timedelta(0)
        else:
           return r


    def exit(self, lunch=True, least=False):
        if not self.is_today():
           return None
        return  (self._now + self.remains(lunch, least)).time()


    def holiday(self):
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


    def working(self):
       if not self.logs() and not self.mission() and self.holiday():
          return False

       # check for holiday
       if self.holiday():
           return False

       # check for total rol day
       if self.rol_total():
          return False

       # check for times
       for k in self.time_for_is_working:
           if self.get_time(k):
               return False

       return True


    def lunch(self):
       value = self._get_hr_data_from_description('IND. MENSA')
       if value:
           return int(float(value))
       else:
           return 0


    def mission(self):
       value = self._get_hr_data_from_description('IND. DI MISSIONE')
       if value:
           return int(float(value))
       else:
           return 0


    def get_time(self, key):
        return self._get_hr_time(self.time_hash[key])


    def rol_total(self):
        """Check for entire day ROL.
           Return bool.
           If holiday return False.
        """
        if self.holiday():
            return False

        _rol_time_seconds = self.get_time('rol').total_seconds()
        if _rol_time_seconds == self._get_hr_work_time():
           return True
        else:
           return False


    def is_today(self):
       if self.date().date() == self._now.date():
          return True
       else:
          return False




def main():

    parser = argparse.ArgumentParser(prog='HRday',
                                     description='HR day manager',
                                     formatter_class=argparse.RawTextHelpFormatter)

    # add HRget arguments parser
    HRget.add_parser(parser)
    # add HRauth arguments parser
    HRauth.add_parser(parser)

    args = parser.parse_args()


    hr_auth = HRauth.HRauth(**vars(args))
    hr_get = HRget.HRget(hr_auth, verbose=False)
    json = hr_get.get(year=args.year, month=args.month, day=args.day)

    day = HRday(json)

    print(day)


if __name__ == '__main__':
    main()

