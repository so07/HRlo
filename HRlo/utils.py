#!/usr/bin/env python3
import re
import argparse
import datetime

from .logs.dayutils import dayutils

def hr2seconds(HRtime):
    """Convert time from HR units to seconds.
       Return seconds in float.
    """
    return float(HRtime) *60.0*60.0

def hr2time(HRtime, format=False):
    """Convert time from HR units to timedelta.
       Return datetime.timedelta.
    """
    dt = datetime.timedelta(seconds=hr2seconds(HRtime))

    if format:
        return dayutils.sec2str(dt.total_seconds())
    else:
        return dt
    #return datetime.timedelta(seconds=hr2seconds(HRtime))

def time_sum(l):
    d = datetime.timedelta(0)
    for i in l:
        is_negative = '-' in i
        if is_negative:
            i = i[1:]
        t = dayutils.str2time(i)
        dt = datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        if is_negative:
            d -= dt
        else:
            d += dt
    return d

class HashedDict (dict):

    def __keytransform__(self, key):
        return self.key_table[key]

    def __keytransforminverse__(self, key):
        for k, v in self.key_table.items():
           if v == key:
              return k

    def __init__(self, key_table={}, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        return super(HashedDict,self).__getitem__(self.__keytransform__(key))

    def __str__(self):
        return str( {self.__keytransforminverse__(k): v for k, v in self.items()} )

    def __repr__(self):
        return repr( {self.__keytransforminverse__(k): v for k, v in self.items()} )

    def _get (self, key):
        return super(HashedDict,self).__getitem__(key)
    def _str (self):
        return super(HashedDict,self).__str__()
    def _repr (self):
        return super(HashedDict,self).__repr__()


def refine_string(_str):
    # remove multiple spaces
    _str = re.sub(' +', ' ', _str)
    return _str

class NameParser(argparse.Action):

     def __call__(self, parser, namespace, values, option_string=None):
         values = [ refine_string(i) for i in values ]
         setattr(namespace, self.dest, values)

class TimeParser(argparse.Action):

     def __call__(self, parser, namespace, values, option_string=None):
         values = [ i.strip() for i in values.split(',') ]
         setattr(namespace, self.dest, values)

