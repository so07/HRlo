#!/usr/bin/env python3
import argparse
from collections import OrderedDict

from .utils import HashedDict

from . import HRauth
from . import HRget

class TotalizatorName:

    from_name_to_HRname = {
        # ... HOLIDAYS ............................
        # Holidays Remainders Previous Year
        'HRPY' : 'FERIE - Residuo AP',
        # Holidays be DUE to
        'HDUE' : 'FERIE - Spettante',
        # Holidays Enjoyed Current Year
        'HECY' : 'FERIE - Goduto Annuo',
        # Holidays TO Enjoy
        'HTOE' : 'FERIE - Da Godere',
        # ... ROL .................................
        # ROL Remainders Previous Year
        'RRPY' : 'ROL - Residuo AP',
        # ROL be DUE to
        'RDUE' : 'ROL - Spettante',
        # ROL Enjoyed Current Year
        'RECY' : 'ROL - Goduto Annuo',
        # ROL TO Enjoy
        'RTOE' : 'ROL - Da Godere',
        # ROL Progressive To Liquidate
        'RPTL' : 'ROL - Liquidate Progressive',
        # ... HOURS ...............................
        # Bank Hours Previous Month
        'BHPM' : 'BANCA ORE - Saldo MP',
        # Bank Hours Current Month
        'BHCM' : 'BANCA ORE - Saldo MC',
        # Amount Hours Previous Month
        'AHPM' : 'MONTE ORE - Saldo MP',
        # Amount Hours Current Month
        'AHCM' : 'MONTE ORE - Saldo MC',
    }

    @classmethod
    def name(self, value):
        for k, v in self.from_name_to_HRname.items():
            if v == value:
                return k 

    @classmethod
    def description(self, value):
        return self.from_name_to_HRname[value]

    @classmethod
    def is_name(self, value):
        return value in self.from_name_to_HRname.keys()

    @classmethod
    def is_description(self, value):
        return value in self.from_name_to_HRname.values()

    @classmethod
    def all_names(self):
        return self.from_name_to_HRname.keys()

    @classmethod
    def all_descriptions(self):
        return self.from_name_to_HRname.values()



class Totalizator (HashedDict):

    from_key_to_HRkey = {
        'name'        : 'CONTATORE',
        'value'       : 'QTACONT',
        'description' : 'DESCRIZIONE',
        'id'          : 'ORDINE',
        'unitmis'     : 'UNITAMIS',
        'contzero'    : 'VISCONTZERO',
        'enable'      : 'ABILITATO',
    }

    def __init__(self, *args, **kwargs):
        self.key_table = self.from_key_to_HRkey
        self.update(*args, **kwargs)

    def __call__(self):
        return self.value()

    def value(self):
        return self['value']

    def description(self):
        return self['description']

    def report(self):
        return "{:30s} = {}".format(self['description'], self['value'])

    def is_holiday(self):
        return 'FERIE' in self['description']

    def is_rol(self):
        return 'ROL' in self['description']

    def is_hours(self):
        return 'ORE' in self['description']



class HRtotalizator (OrderedDict):

    def __init__ (self, json):
        super(HRtotalizator, self).__init__()

        for t in json['Data']:
            _totalizator = Totalizator( {k: v for k, v in zip(json['Fields'], t)} )
            name = TotalizatorName().name(_totalizator.description())
            self[name] = _totalizator

    def report(self):
        return "\n".join([i.report() for i in self.values()])

    def get_totalizator(self, key):
        if TotalizatorName().is_name(key):
            return self[key]
        if TotalizatorName().is_description(key):
            return self[TotalizatorName().name(key)]

    def get_value(self, key):
        totalizator = self.get_totalizator(key)
        if totalizator:
            return totalizator.value()

    def dump(self, file_out):
        pass



def add_parser(parser):

   _parser = parser.add_argument_group('totalizator options')

   _parser.add_argument('--tot', '--totalizators',
                        action = 'store_true',
                        dest = 'totalizators',
                        help='report of totalizators')

   _parser.add_argument('--get-totalizator',
                        #choices = TotalizatorName.all_descriptions(),
                        dest = 'get_totalizator',
                        metavar = 'TOTALIZATOR',
                        help='get totalizator value')


def main():

    parser = argparse.ArgumentParser(prog='HRtotalizator',
                                     formatter_class=argparse.RawTextHelpFormatter)

    add_parser(parser)

    parser.add_argument('--dump',
                        dest = 'file_out',
                        help='dump data to file')

    HRauth.add_parser(parser)

    args = parser.parse_args()

    hr_auth = HRauth.HRauth(**vars(args))

    hr_get = HRget.HRget(hr_auth, verbose=False)

    hr_tot = HRtotalizator(hr_get.totalizators())

    if args.totalizators:
        print(hr_tot.report())

    if args.get_totalizator:
        print(hr_tot.get_value(args.get_totalizator))


if __name__ == '__main__':
   main()

