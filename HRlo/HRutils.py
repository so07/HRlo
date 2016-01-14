#!/usr/bin/env python3
import re
import sys
import datetime
import argparse

from . import utils
from .logs.daylog import DayLog
from .logs.dayutils import dayutils

def add_parser(parser):

   date_parser = parser.add_argument_group('utils options')

   date_parser.add_argument('--time-interval',
                            nargs='*',
                            metavar='HH:MM',
                            help='calculate time intervals.')

   date_parser.add_argument('--hr2seconds',
                            metavar='HRTIME',
                            help='convert time from HR units to seconds.')

   date_parser.add_argument('--hr2time',
                            metavar='HRTIME',
                            help='convert time from HR units to time.')

   date_parser.add_argument('--time-sum',
                            action=utils.TimeParser,
                            metavar='HH:MM:SS',
                            help='calculate time sum.')

def main():

    parser = argparse.ArgumentParser(prog='HRtime',
                                     description='Time useful utilities.',
                                     formatter_class=argparse.RawTextHelpFormatter)

    add_parser(parser)

    args = parser.parse_args()


    if args.time_interval:

        dl = DayLog(datetime.datetime.today(), args.time_interval)

        print("{} = {}".format("Time Interval", dl.uptime()))


    if args.hr2seconds:

        print("{} = {:.0f}".format("Seconds", utils.hr2seconds(args.hr2seconds)) )


    if args.hr2time:

        print("{} = {}".format("Time [HH:MM:SS]", utils.hr2time(args.hr2time, True)) )


    if args.time_sum:
        time_sum = utils.time_sum(args.time_sum)
        print(dayutils.sec2str(time_sum.total_seconds()))


if __name__ == '__main__':
    main()
