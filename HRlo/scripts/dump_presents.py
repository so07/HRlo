#!/usr/bin/env python3
"""
Script for dumping workers presence from HR.
"""
import os
import logging
import datetime
import argparse

from HRlo import HRpresence
from HRlo import HRauth
from HRlo import HRget

from .scripts_utils import logit

defaults = {
    'log_file'   : None,
    #'log_file'   : 'dump_presents.log',
    'csv_prefix' : 'workers_list',
    'csv_dir'    : os.getcwd(),
    'verbose'    : 0,
}


def dump_presents(**kwargs):

    config = {}
    config.update(defaults)
    config.update(kwargs)

    log = logit(**config)

    time_format = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    # make csv dir if not exists
    if not os.path.exists(config['csv_dir']):
        os.makedirs(config['csv_dir'])

    csv_file = '{}_{}.csv'.format(config['csv_prefix'], time_format)
    csv_file = os.path.join(config['csv_dir'], csv_file)

    log.log("getting list of workers")

    hr_auth = HRauth.HRauth()
    hr_get  = HRget.HRget(hr_auth, verbose=False)
    workers = HRpresence.HRpresence(hr_get.presence())

    workers.dump_csv(csv_file)

    log.log("dump data to file: {}".format(csv_file))
    log.log("num workers found {}".format(len(workers.presence)))


def add_parser(parser):

    _parser_dump_presents = parser.add_argument_group('presents options')

    _parser_dump_presents.add_argument('-v', '--verbose',
                                       action='count',
                                       default=0,
                                       help='increase verbosity')

    _parser_dump_presents.add_argument('--csv-prefix',
                                       default=defaults['csv_prefix'],
                                       help='name prefix for csv file. (default %(default)s)')

    _parser_dump_presents.add_argument('--csv-dir',
                                       default=defaults['csv_dir'],
                                       help='directory of csv file. (default %(default)s)')

    _parser_dump_presents.add_argument('--log-file',
                                       default=defaults['log_file'],
                                       help='log file. (default %(default)s)')



def main():

    parser = argparse.ArgumentParser(prog='dump presents',
                                     description=__doc__,
                                     formatter_class=argparse.RawTextHelpFormatter)

    add_parser(parser)

    args = parser.parse_args()

    dump_presents(**vars(args))


if __name__ == '__main__':
    main()

