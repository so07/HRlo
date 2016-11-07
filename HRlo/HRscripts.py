#!/usr/bin/env python3
import re
import sys
import datetime
import argparse

from .scripts import dump_presents, report, monitor

def add_parser(parser):

    _subparsers = parser.add_subparsers(metavar='')

    # dump presents

    _parser_dump_presents = _subparsers.add_parser('dump-presents',
                                                   help=dump_presents.__doc__)

    dump_presents.add_parser(_parser_dump_presents)

    _parser_dump_presents.set_defaults(todo=dump_presents.dump_presents)

    # report

    _parser_report = _subparsers.add_parser('report',
                                            help=report.__doc__)

    report.add_parser(_parser_report)

    _parser_report.set_defaults(todo=report.report)

    # monitor

    _parser_monitor = _subparsers.add_parser('monitor',
                                             help=monitor.__doc__)

    monitor.add_parser(_parser_monitor)

    _parser_monitor.set_defaults(todo=monitor.monitor_daemon)


def main():

    parser = argparse.ArgumentParser(prog='HRscripts',
                                     description='HR useful scripts.',
                                     formatter_class=argparse.RawTextHelpFormatter)

    add_parser(parser)

    args = parser.parse_args()

    dargs=vars(args)

    for k, v in dargs.items():
        if callable(v):
            v(**dargs)


if __name__ == '__main__':
    main()

