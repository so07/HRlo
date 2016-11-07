#!/usr/bin/env python3
"""
Script for report from HR presence.
"""
import os
import re
import glob
import argparse
import configparser
from collections import OrderedDict

from HRlo import HRpresence

from .scripts_utils import logit
from .dump_presents import defaults as dump_presents_defaults


defaults = {
    'log_file'   : None,
    #'log_file'   : 'report.log',
    'csv_prefix' : dump_presents_defaults['csv_prefix'],
    'csv_dir'    : dump_presents_defaults['csv_dir'],
    'config_file' : os.path.join(os.getcwd(), 'report.ini'),
    'verbose'    : 0,
}

def get_values_from_config(config_file, section):
    cfg = configparser.ConfigParser()
    cfg.read(config_file)
    d = {}
    if section in cfg.sections():
        # get value from option
        for key in cfg.options(section):
            # expect quota for values
            d[key] = re.findall('"(.+?)"', cfg.get(section, key))
    return d


def exclude(l, config=None):
    # get dict with key and list of values
    exclude = get_values_from_config(config, 'exclude')
    # exclude workers with key==value from list
    for key, values in exclude.items():
        for v in values:
            l = [ w for w in l if v not in w[key] ]
    return l


def remove(l, config=None):
    # get dict with key and list of values
    remove = get_values_from_config(config, 'remove')
    # remove workers with key==value from list
    for key, values in remove.items():
        for v in values:
            l = [ w for w in l if v not in w[key] ]
    return l


def monitor(l, m, config=None):
    for key, values in get_values_from_config(config, 'monitor').items():
        for v in values:
            if not m.get(v): m[v] = set()
            for w in l:
                if v in w[key]:
                    #if not m.get(v): m[v] = set()
                    m[v].add(w['name'])
    return m


def refine(l, config=None):
    d = {}
    for key, values in get_values_from_config(config, 'refine').items():
        d[key] = {}
        for v in values:
            d[key][v] = [ w for w in l if v in w[key] ]
    return d


def allowed_list(config=None):
    l = []
    for key, values in get_values_from_config(config, 'allowed').items():
        # names of workers
        if key == 'name':
            l.extend(values)
        # files with names of workers
        if key == 'file':
            for f in values:
                if os.path.isfile(f):
                    with open(f, 'r') as fp:
                        name_list = fp.readlines()
                    l.extend([ n.strip() for n in name_list if '#' not in n ])
    return l


def stats_str(l, tot):
    return "{:3d} / {:3d} = {:.1f}%".format(len(l), len(tot), 100.0*len(l)/len(tot))


def report(**kwargs):

    config = {}
    config.update(defaults)
    config.update(kwargs)

    log = logit(**config)

    csv_file = os.path.join(config['csv_dir'], '{}*.csv'.format(config['csv_prefix']))

    list_files = glob.glob(csv_file)

    if not list_files:
        return

    allowed = allowed_list(config.get('config_file'))

    presents_name = set()
    presents_list = []

    dmonitor = {}

    for f in list_files:

        dcsv = HRpresence.HRpresence.read_csv(f)

        p = HRpresence.HRpresence(dcsv)

        list_total = remove(p.presence, config.get('config_file'))

        _presents = [ w for w in p.presence if w.is_present() if w['name'] not in allowed ]

        _presents = remove(_presents, config.get('config_file'))
        _presents = exclude(_presents, config.get('config_file'))

        for w in _presents:
            if w['name'] not in presents_name:
               presents_list.append(w)
            presents_name.add(w['name'])

        monitor(_presents, dmonitor, config.get('config_file'))

    dmonitor = {k: sorted(v) for k, v in dmonitor.items()}

    log.log("{:10s} {}".format('Presents', stats_str(presents_list, list_total)))

    refined_total = refine(list_total, config.get('config_file'))
    refined_presents = refine(presents_list, config.get('config_file'))

    for option, dv in get_values_from_config(config.get('config_file'), 'refine').items():
        for k in dv:
           t = refined_total[option][k]
           l = refined_presents[option][k]
           log.log("{:10s} {}".format(k, stats_str(l, t)))
           if config.get('verbose', 0) > 1:
               log.log(", ".join([i['name'] for i in l]))

    log.log(", ".join(sorted(presents_name)))

    for key, value in dmonitor.items():
        log.log("{:20s}: {}".format(key, stats_str(value, list_total)))
        if config.get('verbose', 0) > 0:
            log.log(", ".join(value))


def add_parser(parser):

    _parser_presents = parser.add_argument_group('get data options')

    _parser_presents.add_argument('-v', '--verbose',
                                  action='count',
                                  default=0,
                                  help='increase verbosity')

    _parser_presents.add_argument('--csv-prefix',
                                  default=defaults['csv_prefix'],
                                  help='name prefix for csv file. (default %(default)s)')

    _parser_presents.add_argument('--csv-dir',
                                  default=defaults['csv_dir'],
                                  help='directory of csv file. (default %(default)s)')

    _parser_presents.add_argument('--log-file',
                                  default=defaults['log_file'],
                                  help='log file. (default %(default)s)')

    _parser_presents.add_argument('--config-file',
                                  default=defaults['config_file'],
                                  help='configuration file. (default %(default)s)')


def main():

    parser = argparse.ArgumentParser(prog='HR report',
                                     description=__doc__,
                                     formatter_class=argparse.RawTextHelpFormatter)

    add_parser(parser)

    args = parser.parse_args()

    report(**vars(args))


if __name__ == '__main__':
    main()

