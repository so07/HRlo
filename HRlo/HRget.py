#!/usr/bin/env python3
import re
import sys
import requests
import datetime
import calendar
import argparse
import json

from collections import OrderedDict

from .logs.dayutils  import dayutils
from .utils import NameParser

from . import HRauth

class HRget(object):

    def __init__(self, HRauth, verbose=False):
        self.verbose = verbose
        self.host = HRauth.host()

        # set URLs
        self.login_url    = 'https://' + self.host + '/HRPortal/servlet/cp_login'
        self.sheet_url    = 'https://' + self.host + '/HR-WorkFlow/servlet/hfpr_bcapcarte'
        self.post_url     = 'https://' + self.host + '/HR-WorkFlow/servlet/SQLDataProviderServer'
        self.portal_url   = 'https://' + self.host + '/HRPortal/servlet/SQLDataProviderServer'
        self.presence_url = 'https://' + self.host + '/HRPortal/servlet/Report?ReportName=AAA_ElencoPresenti&m_cWv=Rows%3D0%0A0%5Cu0023m_cMode%3Dhyperlink%0A0%5Cu0023outputFormat%3DCSV%0A0%5Cu0023pageFormat%3DA4%0A0%5Cu0023rotation%3DLANDSCAPE%0A0%5Cu0023marginTop%3D7%0A0%5Cu0023marginBottom%3D7%0A0%5Cu0023marginLeft%3D7%0A0%5Cu0023hideOptionPanel%3DT%0A0%5Cu0023showAfterCreate%3DTrue%0A0%5Cu0023mode%3DDOWNLOAD%0A0%5Cu0023ANQUERYFILTER%3D1%0A0%5Cu0023pRAPPORTO%3D%0A0%5Cu0023pFILIALE%3D%0A0%5Cu0023pUFFICIO%3D%0A0%5Cu0023m_cParameterSequence%3Dm_cMode%2CoutputFormat%2CpageFormat%2Crotation%2CmarginTop%2CmarginBottom%2CmarginLeft%2Cmode%2ChideOptionPanel%2CshowAfterCreate%2CANQUERYFILTER%2CpRAPPORTO%2CpFILIALE%2CpUFFICIO%0A'

        # set employee
        self.username = HRauth.username()
        self.password = HRauth.password()
        self.idemploy = "{:0>7}".format(str(HRauth.idemploy()))
        #print(self.idemploy)

        if self.verbose > 1:
           print (">>>USERNAME>>>", self.username)
           print (">>>IDEMPLOY>>>", self.idemploy)
           #print ("[{}]@{}".format(__class__.__name__, sys._getframe().f_code.co_name))

        self.session = requests.Session()
        self.cookies = None 

        self.login()

    def login(self):
        auth = {'m_cUserName' : self.username, 'm_cPassword' : self.password, 'm_cAction' : 'login'}
        r = self.session.post(self.login_url, params=auth, allow_redirects=False)
        self.cookies = r.cookies

        if self.verbose > 1:
           print (">>>CODE>>>", r.status_code)
           print (">>>HISTORY>>>", r.history)
           print (">>>HEADERS>>>", r.headers)
           print (">>>COOKIES>>>", r.cookies)
           print (">>>LOCATION>>>", r.headers['location'])
           #print (">>>PAGE>>>", r.text)

        try:
           if 'jsp/home.jsp' in r.headers['location']:
              pass
        except:
           print("\n[HRget] *** ERROR *** on HR authentication!\n")
           sys.exit(1)

    def get_range(self, day_range):
       data = []
       # loop over months of day_range
       for y, m in day_range.months():

          # get month data from HR
          full_month = self.get(y, m)

          # get first and last days for month
          first, last = dayutils.month_bounds( datetime.date(y, m, 1) )
          # to avoid future day: if same month of today's month set last day to today
          if dayutils.is_same_month( datetime.datetime(y, m, 1), datetime.datetime.today() ):
             last = datetime.datetime.today().date()
          # list of month days within day_range
          l = [ i.day for i in dayutils.day_range(first, last) if i in day_range ]
          # extract days within day_range from data of all month
          old_data = full_month['Data']
          data += [ old_data[i-1] for i in l ]

          # save fields
          fields = full_month['Fields']

       if data:
         jret = {'Fields' : fields, 'Data' : data}
         return jret


    def _check_data(self, d, year, month, day):

        if len(d) < 1:
            print("[HRget] ***ERROR***")
            print("Data not found in date {}-{}".format(year, month) )
            sys.exit(-1)


    def get(self, year  = datetime.datetime.today().year,
                  month = datetime.datetime.today().month,
                  day   = None):

        str_month = "{:0>2}".format(month)
        str_year  = "{:d}".format(year)

        num_days_in_month = calendar.monthrange(year, month)[1]

        last_day = num_days_in_month
        if dayutils.is_same_month( datetime.datetime(year, month, 1), datetime.datetime.today() ):
           last_day = datetime.datetime.today().day

        if self.verbose > 1:
            print (">>>NUMDAYMONTH>>>", num_days_in_month)
            print (">>>LASTDAY>>>", last_day)

        # COOKIES {{{
        cookies = self.cookies
        # }}}
        # HEADERS {{{
        headers = {
                   'Pragma': 'no-cache',
                   'Cache-Control': 'no-cache'
                  }
        # }}}
        # PARAMS  {{{
        params = {
                  'rows' : 300,
                  'startrow' : '0',
                  'count' : 'false',
                  'cmdhash':'89ff07d888efecba391f40eac7d04e9a',
                  'sqlcmd' : 'rows:hfpr_fcartellino3',
                  'IDCOMPANY':'000001',
                  'IDEMPLOY': self.idemploy,
                  'Anno': str_year,
                  'Mese': str_month,
                  'Visualiz':'N',
                  'LaFlexi':'N',
                  'LaFlexiProg':'N',
                  'VisDescr':'',
                  'DADRATIM':'',
                  'DATTMI':'',
                  'HHMM':'',
                  'ImportVoci':'S',
                  'p_NOEDIT_1':'',
                  'p_NOEDIT_2':'',
                  'p_NOEDIT_3':'',
                  'p_NOEDIT_4':'',
                  'p_ADMIN':'',
                  'gCarOri':'N',
                  'gVismmAtt':'',
                  'TACART':'N',
                  'vIDPLANTB':'99999',
                  'vIDPRESGRP':'',
                  'NUMERORIGHE':'2',
                  'StringaCol':'01S&&&02S&&&03S&&&04S&&&05S&&&06S&&&07S&&&08S&&&09N&&&10N&&&11N&&&12N&&&13N&&&14N&&&15N&&&16N&&&17N&&&',
                  'SchedeLavoro':'N',
                  'pFILESITO':'',
                  'pFILGIUS':'0',
                  'TOTHORD':'S',
                  'TOTHECC':'',
                  'TOTFLEX':'',
                  'ABILITANOTESPESE':'N',
                  'TIPONOTESPESE':'1',
                  'ABILITATIMESHEET':'N'
                 }
        # }}}

        p = self.session.post(self.sheet_url, cookies=cookies)

        p = self.session.post(self.post_url, headers=headers, cookies=cookies, params=params)


        d = p.json()['Data'][:last_day]
        f = p.json()['Fields']

        self._check_data(d, year, month, day)

        if day:
            d = d[day-1]
        
        if self.verbose > 1:
            print ('>>>FIELDS>>>', f)
            print ('>>>DATA>>>', d)

            #for i, item in enumerate(f):
            #    print( item, ' = ', d[i])

        json = {'Fields' : f, 'Data' : d}

        return json


    def totalizators(self,
                     year  = datetime.date.today().year,
                     month = datetime.date.today().month):

        date = datetime.date(year, month, 1) + datetime.timedelta(days=calendar.monthrange(year, month)[1])

        # COOKIES {{{
        cookies = self.cookies
        # }}}
        # HEADERS {{{
        headers = {
                   'Pragma': 'no-cache',
                   'Cache-Control': 'no-cache'
                  }
        # }}}
        # PARAMS {{{
        params = {
                  'rows' : 100,
                  'startrow' : '0',
                  'count' : 'false',
                  'cmdhash':'2e2926382311a0b72e72cd1e1cdc4ccc',
                  'sqlcmd' : 'rows:hfpr_fgadgetconta',
                  'pIDEMPLOY': self.idemploy,
                  'pIDCOMPANY':'000001',
                  'pDATA':date,
                  'pADMIN':'',
                 }
        # }}}

        p = self.session.post(self.sheet_url, cookies=cookies)

        p = self.session.post(self.post_url, headers=headers, cookies=cookies, params=params)

        d = p.json()['Data'][:-1]
        f = p.json()['Fields']

        json = {'Fields' : f, 'Data' : d}

        return json


    def phone(self, names = [], phones = []):

        re_names = [ re.compile(i.upper()) for i in names ]
        re_phones = [ re.compile(i.upper()) for i in phones ]

        fields_name = ['ANSURNAM']
        fields_phone = ['ANTELEF', 'ANMOBILTEL']

        fields_to_return = ['ANSURNAM', 'ANEMAIL', 'ANTELEF', 'ANMOBILTEL']
        data_to_return   = []


        # COOKIES {{{
        cookies = self.cookies
        # }}}
        # HEADERS {{{
        headers = {
                   'Pragma': 'no-cache',
                   'Cache-Control': 'no-cache'
                  }
        # }}}
        # PARAMS  {{{
        params = {
                  'rows'      : '2000',
                  'startrow'  : '0',
                  'count'     : 'true',
                  'cmdhash'   : 'b55cc94f7a3a372690c14949975ac422',
                  'sqlcmd'    : 'q_rubrica',
                  'pANSURNAM' : '',
                 }
        # }}}

        p = self.session.post(self.portal_url, headers=headers, cookies=cookies, params=params)

        try:
           list_phone = p.json()['Data'][:-1]
        except:
           return OrderedDict()

        fields_ = p.json()['Fields']

        # convert data to ordered dict

        json_ = {}

        for worker in list_phone:
           json = {k: v for k, v in zip(fields_, worker)}
           l = []
           for k in fields_to_return:
              if json.get(k):
                 l.append(json[k])
           data_to_return.append(l)

        json_['Fields'] = fields_to_return
        json_['Data']   = data_to_return


        # filter data
        if re_names or re_phones:
           l = []
           for i in json_['Data']:
               _name  = i[0]
               _phone = " ".join( [ re.sub(r"[^0-9]+", "", j) for j in i[2:] ] )
               l.extend( [ i for r in re_names if r.search(_name) ] )
               l.extend( [ i for r in re_phones if r.search(_phone) ] )

           json_['Data'] = l

        return json_

#{{{ deprecated
    def phone_old(self, names):

        fields_to_return = ['ANSURNAM', 'ANEMAIL', 'ANTELEF', 'ANMOBILTEL']
        data_to_return   = []

        for n in names:

            name = n.upper()

            # COOKIES {{{
            cookies = self.cookies
            # }}}
            # HEADERS {{{
            headers = {
                       'Pragma': 'no-cache',
                       'Cache-Control': 'no-cache'
                      }
            # }}}
            # PARAMS  {{{
            params = {
                      'rows'      : '5',
                      'startrow'  : '0',
                      'count'     : 'true',
                      'cmdhash'   : '8a0d2d1c35e16e1e2135a25505b5dd32',
                      'sqlcmd'    : 'q_rubrica',
                      'queryfilter' :"ANSURNAM like '" + name + "%'",
                      'pANSURNAM' : '',
                     }
            # }}}

            p = self.session.post(self.portal_url, headers=headers, cookies=cookies, params=params)

            try:
               list_phone = p.json()['Data'][:-1]
            except:
               return OrderedDict()

            fields_ = p.json()['Fields']

            # convert data to ordered dict

            json_ = {}

            for worker in list_phone:
               json = {k: v for k, v in zip(fields_, worker)}
               l = []
               for k in fields_to_return:
                  if json.get(k):
                     l.append(json[k])
               data_to_return.append(l)

        json_['Fields'] = fields_to_return
        json_['Data']   = data_to_return

        return json_
#}}}


    def presence(self):

        p = self.session.get(self.presence_url)

        csv_data = p.text

        return csv_data




def add_parser(parser):

   date_parser = parser.add_argument_group('date options')

   date_parser.add_argument('-d', '--day',
                            default = datetime.datetime.today().day, type=int,
                            help='select day')

   date_parser.add_argument('-m', '--month',
                            default = datetime.datetime.today().month, type=int,
                            help='select month')

   date_parser.add_argument('-y', '--year',
                            default = datetime.datetime.today().year, type=int,
                            help='select year')


def add_parser_phone(parser):

   phone_parser = parser.add_argument_group('phone number options')

   phone_parser.add_argument('-p', '--phone',
                             dest = 'phone_name',
                             default = [],
                             nargs = '+',
                             action = NameParser,
                             metavar = "SURNAME",
                             help="get phone number")

   phone_parser.add_argument('-n', '--name-from-phone',
                             dest = 'phone_number',
                             default = [],
                             nargs = '+',
                             metavar = "PHONE",
                             help="get name from phone number")


def main ():

    parser = argparse.ArgumentParser(prog='HRget',
                                     description='',
                                     formatter_class=argparse.RawTextHelpFormatter)

    add_parser(parser)
    add_parser_phone(parser)

    parser.add_argument('-v', '--verbose',
                        action="count", default=0,
                        help="increase verbosity")

    parser.add_argument('-g', '--get',
                        action='store_true',
                        help="get day")

    parser.add_argument('--totalizators',
                        action='store_true',
                        help="get totalizators")

    parser.add_argument('--presence',
                        action='store_true',
                        help="get presence of worker")

    parser.add_argument('--dump',
                        dest = 'file_out',
                        help="dump to file")

    HRauth.add_parser(parser)

    args = parser.parse_args()


    auth = HRauth.HRauth(**vars(args))

    hr_get = HRget(auth, verbose=args.verbose)


    if args.get:

        djson = hr_get.get(year=args.year, month=args.month, day=args.day)

        if args.verbose:
            for k, v in zip(djson['Fields'], djson['Data']):
                print(k, " = ", v)

        if args.file_out:
            with open(args.file_out, 'w') as f:
                json.dump(djson, f)
            #with open(args.file_out, 'r') as f:
            #    djson = json.load(f)


    if args.totalizators:

        djson = hr_get.totalizators(year=args.year, month=args.month)

        if args.verbose:
            for d in djson['Data']:
                for k, v in zip(djson['Fields'], d):
                    print(k, " = ", v)
                print()

        if args.file_out:
            with open(args.file_out, 'w') as f:
                json.dump(djson, f)


    if args.phone_name or args.phone_number:

        djson = hr_get.phone(names = args.phone_name, phones = args.phone_number)

        print()
        for d in djson['Data']:
            for k, v in zip(djson['Fields'], d):
                print(v)
            print()

        if args.file_out:
            with open(args.file_out, 'a') as f:
                json.dump(djson, f)


    if args.presence:

        csv = hr_get.presence()

        if args.verbose:
            print(csv)

        if args.file_out:
            with open(args.file_out, 'w') as f:
                f.write(csv)



if __name__ == '__main__':
    main()

