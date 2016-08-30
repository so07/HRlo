#!/usr/bin/env python3
import re
import argparse
from collections import OrderedDict

from . import HRauth
from . import HRget
from . import utils


class HRphone (OrderedDict):


    def __init__ (self, json):
        super(HRphone, self).__init__()

        self.json = self._json_to_dict(json)


    def _json_to_dict(self, arg_json):
        """Refine data from original json."""

        fields_to_return = ['ANSURNAM', 'ANEMAIL', 'ANTELEF', 'ANMOBILTEL']
        data_to_return   = []

        _json = {}

        for worker in arg_json['Data']:
           j= {k: v for k, v in zip(arg_json['Fields'], worker)}
           l = []
           for k in fields_to_return:
              if j.get(k):
                 l.append(j[k])
           data_to_return.append(l)

        _json['Fields'] = fields_to_return
        _json['Data']   = data_to_return

        return _json


    def get(self, names=[], phones=[]):
        """Filter data with names in names list or phone number in phones list.
           Return json with filtered workers info."""
        re_names = [ re.compile(i.upper()) for i in names ]
        re_phones = [ re.compile(i.upper()) for i in phones ]

        _json = {'Fields': self.json['Fields'], 'Data': self.json['Data']}

        # filter data
        if re_names or re_phones:
           l = []
           for i in self.json['Data']:
               _name  = i[0]
               _phone = " ".join( [ re.sub(r"[^0-9]+", "", j) for j in i[2:] ] )
               l.extend( [ i for r in re_names if r.search(_name) ] )
               l.extend( [ i for r in re_phones if r.search(_phone) ] )
           _json['Data'] = l

        return _json


    def report(self, names=[], phones=[]):
        """Return string report of workers filtered accordingly to names in names list and phone number in phones list.""" 

        djson = self.get(names, phones)

        l = []
        for d in djson['Data']:
            l.append('')
            for k, v in zip(djson['Fields'], d):
                l.append(v)

        if l:
            return '\n'.join(l) + '\n'
        else:
            return ''



def add_parser(parser):

   phone_parser = parser.add_argument_group('phone number options')

   phone_parser.add_argument('-p', '--phone',
                             dest = 'phone_name',
                             default = [],
                             nargs = '+',
                             action = utils.NameParser,
                             metavar = "SURNAME",
                             help="get phone number")

   phone_parser.add_argument('-n', '--name-from-phone',
                             dest = 'phone_number',
                             default = [],
                             nargs = '+',
                             metavar = "PHONE",
                             help="get name from phone number")



def main():

    parser = argparse.ArgumentParser(prog='HRphone',
                                     description='HR manager utility for workers phone number.',
                                     formatter_class=argparse.RawTextHelpFormatter)

    add_parser(parser)

    HRauth.add_parser(parser)

    args = parser.parse_args()


    hr_auth = HRauth.HRauth(**vars(args))

    hr_get = HRget.HRget(hr_auth, verbose=False)

    hr_phone = HRphone(hr_get.phone())


    if args.phone_name or args.phone_number:
        print(hr_phone.report(names = args.phone_name, phones = args.phone_number))



if __name__ == '__main__':
   main()

