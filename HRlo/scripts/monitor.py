#!/usr/bin/env python3
"""
Script for HR monitoring.
"""
import time
import logging
import argparse
import datetime

from .dump_presents import dump_presents
from .report import report
from .scripts_utils import logit
from .dump_presents import defaults as dump_presents_defaults
from .report import defaults as report_defaults

time_format = '%Y-%m-%d/%H:%M'

defaults = {
    'log_file' : 'monitor.log',
    'csv_prefix'   : dump_presents_defaults['csv_prefix'],
    'csv_dir'      : dump_presents_defaults['csv_dir'],
    'config_file'  : report_defaults['config_file'],
    'verbose'      : 0,
    'monitor_freq' : 30,
    'monitor_start': datetime.datetime.now().strftime(time_format),
    'monitor_end'  : (datetime.datetime.now()+datetime.timedelta(days=1)).strftime(time_format),
}

def monitor_daemon(**kwargs):

    config = {}
    config.update(defaults)
    config.update(kwargs)

    log = logit(**config)

    log.log("----- monitor daemon {} -----".format(datetime.datetime.now()))
    log.log("starting monitor daemon")
    log.log("start @ {}".format(config['monitor_start']))
    log.log("end @ {}".format(config['monitor_end']))
    log.log("frequency in minutes {}".format(config['monitor_freq']))

    while datetime.datetime.now() < datetime.datetime.strptime(config['monitor_end'], time_format):

        if datetime.datetime.now() > datetime.datetime.strptime(config['monitor_start'], time_format) and \
           datetime.datetime.now() < datetime.datetime.strptime(config['monitor_end'], time_format):

            log.log("dumping presents")

            try:
                dump_presents(**config)
            except Exception as e:
                log.log("dump_presents ends with ERROR: " + str(e))

            log.log("getting data")
            log.log("RESULTS @{}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

            try:
                report(datefmt='-', **config)
            except Exception as e:
                log.log("report ends with ERROR: " + str(e))

        log.log("waiting next pool @ " + str(datetime.datetime.now()+datetime.timedelta(minutes=config['monitor_freq'])))

        try:
            time.sleep(config['monitor_freq']*60)
        except Exception as e:
            log.log("waiting ends with ERROR: " + str(e))



def add_parser(parser):

    _parser_monitor_daemon = parser.add_argument_group('monitor daemon options')

    _parser_monitor_daemon.add_argument('-v', '--verbose',
                                        action='count',
                                        default=0,
                                        help='increase verbosity')

    _parser_monitor_daemon.add_argument('--csv-prefix',
                                        default=defaults['csv_prefix'],
                                        help='name prefix for csv file. (default %(default)s)')

    _parser_monitor_daemon.add_argument('--csv-dir',
                                        default=defaults['csv_dir'],
                                        help='directory of csv file. (default %(default)s)')

    _parser_monitor_daemon.add_argument('--log-file',
                                        default=defaults['log_file'],
                                        help='log file. (default %(default)s)')

    _parser_monitor_daemon.add_argument('--start',
                                        dest='monitor_start',
                                        default=defaults['monitor_start'],
                                        help='monitor start. time format is YYYY-MM-DD/HH:MM. (default %(default)s)')

    _parser_monitor_daemon.add_argument('--end',
                                        dest='monitor_end',
                                        default=defaults['monitor_end'],
                                        help='monitor end. time format is YYYY-MM-DD/HH:MM. (default %(default)s)')

    _parser_monitor_daemon.add_argument('--freq',
                                        dest='monitor_freq',
                                        default=defaults['monitor_freq'],
                                        type=int,
                                        help='monitor frequencein minutes. (default %(default)s)')



def main():

    parser = argparse.ArgumentParser(prog='HR monitor',
                                     description=__doc__,
                                     formatter_class=argparse.RawTextHelpFormatter)

    add_parser(parser)

    args = parser.parse_args()

    monitor_daemon(**vars(args))


if __name__ == '__main__':
    main()

