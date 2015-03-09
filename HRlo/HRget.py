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
                   'Host': self.host,
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                   'Referer': self.sheet_url,
                   'Connection': 'keep-alive',
                   'Pragma': 'no-cache',
                   'Cache-Control': 'no-cache'
                  }
        # }}}
        # PARAMS  {{{
                  #'IDEMPLOY': self.idemploy,
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

        return f, d


def debug ():

    import HRauth

    a = HRauth.HRauth()
    h = HRget(a, verbose=True)

    #f, d = h.get()
    f, d = h.get(day=2)
    #f, d = h.get(2015, 3, 3)
    f, d = h.get(month=2)


if __name__ == '__main__':
    debug()
