#!/usr/bin/env python3
import re
import csv
import argparse
import itertools

from .utils import HashedDict, NameParser

from . import HRauth
from . import HRget

class presence (HashedDict):

    from_key_to_HRkey = {
        'date'           : 'Date()'                                            , 
        'name'           : 'AAA_ElencoPresenti.c_Cognome_Nome'                 , 
        'office'         : 'AAA_ElencoPresenti.c_Sede'                         , 
        'room'           : 'AAA_ElencoPresenti.c_Stanza'                       , 
        'boss'           : 'AAA_ElencoPresenti.c_Resp_Struttura_Organizzativa' , 
        'status'         : 'AAA_ElencoPresenti.c_Presente'                     , 
        'state'          : 'AAA_ElencoPresenti.c_IdStateOggi'                  , 
        'proof'          : 'AAA_ElencoPresenti.c_GiustOggi'                    , 
        'city'           : 'AAA_ElencoPresenti.c_IdProvOggi'                   , 
        'email'          : 'AAA_ElencoPresenti.c_E_mail'                       , 
        'phone'          : 'AAA_ElencoPresenti.c_Tel_Interno'                  , 
        'company phone'  : 'AAA_ElencoPresenti.c_Cell_Aziendale'               , 
        'department'     : 'AAA_ElencoPresenti.c_Struttura_Organizzativa'      , 
        'state tomorrow' : 'AAA_ElencoPresenti.c_IdStateDom'                   , 
        'proof tomorrow' : 'AAA_ElencoPresenti.c_GiustDom'                     , 
        'city tomorrow'  : 'AAA_ElencoPresenti.c_IdProvDom'                    , 
    }

    def __init__(self, *args, **kwargs):
        self.key_table = self.from_key_to_HRkey
        self.update(*args, **kwargs)

    def report (self):
        s  = "{} : {} {}\n".format(self['name'], self['status'], self['proof'])
        s += "{}\n".format(self['email'])
        s += "{}  {}\n".format(self['phone'], self['company phone'])
        s = """{} : {}  {} {} {}
        {}
        {} {}
        {}  @[{}]
        {}  ({})""".format(
            self['name'],
            self['status'], self['proof'], self['city'], self['state'],
            self['email'],
            self['phone'], self['company phone'],
            self['office'], self['room'],
            self['department'], self['boss'],
            )
        if self['proof tomorrow'] or self['city tomorrow'] or self['state tomorrow']:
            s += """
        TOMORROW: {} {} {}""".format(self['proof tomorrow'], self['city tomorrow'], self['state tomorrow'])
        return s

    def is_like (self, key, value):
        m = re.search(value.upper(), self[key].upper())
        if m:
            return True
        else:
            return False

    def is_present(self):
        pass

    def is_at(self, city):
        pass


class HRpresence (object):

    def __init__ (self, csv_data):
        self.csv_data = csv_data
        self.raw_presence = [ presence(r) for r in self._csv_read(csv_data) ]
        self.presence = self._csv_refine()

    def _csv_refine(self):

        name_unique = set([ i['name'] for i in self.raw_presence ])

        _workers = []
        _refined = []

        # loop on raw data
        for w in self.raw_presence:
            if w['name'] not in _workers:
                _workers.append(w['name'])
                _refined.append(w)

        return _refined
        
    def _csv_read(self, csv_data):
        # convert csv data from string to list
        list_csv_data = csv_data.split('\n')
        #reader = csv.reader(list_csv_data, delimiter=';')
        reader = csv.DictReader(list_csv_data, delimiter=';')
        return reader

    def _cvs_write(self):
        pass

    def dump_csv(self, file_out):
        with open(file_out, 'w') as f:
            f.write(self.csv_data)

    @classmethod
    def read_csv(self, file_input):
        with open(file_input, 'r') as f:
            csv_data = f.read()
        return csv_data


    def dump_data(self, file_out, raw=True):
        pass

    def __len__(self):
        return len(self.presence)
        return len(self.raw_presence)

    def get (self, key, value='', raw=False):
        data = self.presence
        if raw:
            data = self.raw_presence
        return [ i for i in data if i.is_like(key, value) ]

    def get_all (self, key, value=''):
        s = set( [ i[key] for i in self.get(key, value) ] )
        return sorted(list(s))

    def get_zip_keys (self, keys):
        r = [ [] ] * len(self)
        for k in keys:
            l = [ [ i[k] ] for i in self.get(k) ]
            r = [ l2+l1  for l1, l2 in itertools.zip_longest(l, r) ]
        # return unique lists in list
        return list(k for k,_ in itertools.groupby(sorted(r)))

    def get_zip (self, keys, values=[]):
        r = []
        zip_keys = self.get_zip_keys(keys)
        if not values or not [ i for i in values if i ]:
            return zip_keys
        for value_from_worker in zip_keys:
            add_value = True
            counter_keys = 0
            for k, value_from_args in itertools.zip_longest(keys, values):
                if not value_from_args:
                    value_from_args = ''
                if not value_from_args.upper() in value_from_worker[counter_keys].upper():
                    add_value = False
                counter_keys += 1
            if add_value:
                r.append(value_from_worker)
        # return unique lists in list
        return list(k for k,_ in itertools.groupby(sorted(r)))

    def report(self, name):
        workers = self.get('name', name)
        s = '\n'
        for w in workers:
           s += w.report()
           s += '\n'
        return s



def add_parser(parser):

   _parser = parser.add_argument_group('presence options')

   _parser.add_argument('--in', '--is_present',
                        dest = 'presence',
                        nargs='+',
                        action = NameParser,
                        metavar = 'SURNAME',
                        help='get report on worker')



def main():

    parser = argparse.ArgumentParser(prog='HRpresence',
                                     description='',
                                     formatter_class=argparse.RawTextHelpFormatter)

    add_parser(parser)

    parser.add_argument('--dump',
                        dest = 'file_out',
                        help='dump data to file in csv format')

    parser.add_argument('--read',
                        dest = 'file_input',
                        help='read data from file in csv format')

    HRauth.add_parser(parser)

    args = parser.parse_args()


    if args.file_input:

        csv_data = HRpresence.read_csv(args.file_input)

    else:

        auth = HRauth.HRauth(**vars(args))

        h = HRget.HRget(auth, verbose=False)

        # get presence in scv format
        csv_data = h.presence()


    p = HRpresence(csv_data)

    if args.presence:
        for name in args.presence:
            print(p.report(name))

    if args.file_out:
        p.dump_csv(args.file_out)


if __name__ == '__main__':
   main()

