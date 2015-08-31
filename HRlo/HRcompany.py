#!/usr/bin/env python3
import csv
import argparse
import itertools

from HRlo.utils import HashedDict

from . import HRauth
from . import HRget
from . import HRpresence


def add_parser(parser):

   _parser = parser.add_argument_group()

   _parser.add_argument('--report',
                        action="store_true",
                        help="report of company")

   _parser.add_argument('--key',
                        dest = 'key',
                        nargs ='+',
                        help='get key')

   _parser.add_argument('--value',
                        dest = 'value',
                        nargs ='+',
                        help='get value')

   _parser.add_argument('-v', '--verbose',
                        action="count", default=0,
                        help="increase verbosity")




def main():

    parser = argparse.ArgumentParser(prog='HRcompany',
                                     description='',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    add_parser(parser)

    HRauth.add_parser(parser)

    args = parser.parse_args()

    auth = HRauth.HRauth(**vars(args))

    h = HRget.HRget(auth, verbose=False)

    # get presence in scv format
    csv_data = h.presence()

    p = HRpresence.HRpresence(csv_data)

    if args.report:

        workers    = p.get_all('name')
        bosses     = p.get_all('boss')
        department = p.get_all('department')
        office     = p.get_all('office')

        print("Number of workers    =", len(workers))
        if args.verbose > 1:
            print("   >>>", ", ".join(workers))

        print("Number of bosses     =", len(bosses))
        if args.verbose:
            print("   >>>", ", ".join(bosses))

        print("Number of department =", len(department))
        if args.verbose:
            print("   >>>", ", ".join(department))

        print("Number of office     =", len(office))
        if args.verbose:
            print("   >>>", ", ".join(office))


    if args.key or args.value:

           l = p.get_zip(args.key, args.value)

           print("Number of element =", len(l))

           for i in l:
               print(" - ".join(i))


if __name__ == '__main__':
   main()
