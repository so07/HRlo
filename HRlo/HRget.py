#!/usr/bin/env python3
import re
import sys
import requests
import datetime
import calendar

from logs import dayutils

class HRget(object):

    def __init__(self, HRauth, verbose=False):
        self.verbose = verbose
        self.host = HRauth.host()
        # set URLs
        self.login_url = 'https://' + self.host + '/HRPortal/servlet/cp_login'
        self.sheet_url = 'https://' + self.host + '/HR-WorkFlow/servlet/hfpr_bcapcarte'
        self.post_url  = 'https://' + self.host + '/HR-WorkFlow/servlet/SQLDataProviderServer'
        # set employee
        self.username = HRauth.username()
        self.password = HRauth.password()
        self.idemploy = "{:0>7}".format(str(HRauth.idemploy()))
        #print(self.idemploy)

        if self.verbose:
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

        if self.verbose:
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


    def get(self, year  = datetime.datetime.today().year,
                  month = datetime.datetime.today().month,
                  day   = None):


        str_month = "{:0>2}".format(month)
        str_year  = "{:d}".format(year)


        num_days_in_month = calendar.monthrange(year, month)[1]

        last_day = num_days_in_month
        if dayutils.is_same_month( datetime.datetime(year, month, 1), datetime.datetime.today() ):
           last_day = datetime.datetime.today().day

        if self.verbose:
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

        if day:
            d = d[day-1]
        
        if self.verbose:
            print ('>>>FIELDS>>>', f)
            print ('>>>DATA>>>', d)

            #for i, item in enumerate(f):
            #    print( item, ' = ', d[i])

        json = {'Fields' : f, 'Data' : d}

        return json


def add_parser(parser):

   date_parser = parser.add_argument_group('Date options')

   date_parser.add_argument('-d', '--day',
                            default = datetime.datetime.today().day, type=int,
                            help='select day')

   date_parser.add_argument('-m', '--month',
                            default = datetime.datetime.today().month, type=int,
                            help='select month')

   date_parser.add_argument('-y', '--year',
                            default = datetime.datetime.today().year, type=int,
                            help='select year')


def main ():

    import argparse
    import HRauth

    parser = argparse.ArgumentParser(prog='HRget',
                                     description='',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    add_parser(parser)

    parser.add_argument('-v', '--verbose',
                        action="count", default=0,
                        help="increase verbosity")

    parser.add_argument('--dump',
                        dest = 'file_out',
                        help="dump to file")

    HRauth.add_parser(parser)

    args = parser.parse_args()


    auth = HRauth.HRauth(**vars(args))

    h = HRget(auth, verbose=args.verbose)

    djson = h.get(year=args.year, month=args.month, day=args.day)

    if args.file_out:
        import json
        with open(args.file_out, 'w') as f:
            json.dump(djson, f)
        #with open(args.file_out, 'r') as f:
        #    djson = json.load(f)

    if args.verbose:
       for k, v in zip(djson['Fields'], djson['Data']):
          print(k, " = ", v)


if __name__ == '__main__':
    main()
