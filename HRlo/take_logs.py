#!/usr/bin/env python
import argparse
import datetime

HR_fmt_time = "%H.%M"
HR_fmt_day  = "%Y-%m-%d"

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    it = iter(iterable)
    return zip(it, it)

def main():

    parser = argparse.ArgumentParser(prog='',
                                     description='',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-v", "--verbose",
                        action="count", default=0,
                        help="increases verbosity.") 

    parser.add_argument('logs',
                        nargs='+',
                        help='logs')

    args = parser.parse_args()


    HR_workday = datetime.timedelta(hours=7, minutes=12)


    now = datetime.datetime.today()

    logs = [ datetime.datetime.strptime(now.strftime(HR_fmt_day)+i, HR_fmt_day+HR_fmt_time) for i in args.logs ]
    logs.append( now )


    uptime = datetime.timedelta(0)

    for i, o in pairwise(logs):
        d = o-i
        if args.verbose:
           print 'IN', i.time(), 'OUT', o.time(), 'UPTIME', d
        uptime += d

    print 'Uptime   ', uptime

    if len(logs)%2 ==0:
       print 'Remain   ', HR_workday-uptime
       print 'Est.exit ', now+(HR_workday-uptime)


if __name__ == '__main__':
    main()

