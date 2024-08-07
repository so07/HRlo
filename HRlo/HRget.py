#!/usr/bin/env python3
import re
import sys
import datetime
import calendar
import argparse
import json

from collections import OrderedDict

from .logs.dayutils  import dayutils

from . import HRauth

class HRget(object):

    def __init__(self, HRauth, verbose=False, debug=False):

        self.HRauth = HRauth
        self.verbose = verbose

        # set URLs
        self.sheet_url    = 'https://' + self.HRauth.host() + '/HR-WorkFlow/servlet/hfpr_bcapcarte'
        self.sheet_url    = 'https://' + self.HRauth.host() + '/HR-WorkFlow/servlet/hfpr_fcartellino_day'
        self.post_url     = 'https://' + self.HRauth.host() + '/HR-WorkFlow/servlet/SQLDataProviderServer'
        self.portal_url   = 'https://' + self.HRauth.host() + '/HRPortal/servlet/SQLDataProviderServer'
        self.hash_url     = 'https://' + self.HRauth.host() + '/HRPortal/jsp/gsmd_one_column_model.jsp'
        self.presence_url = 'https://' + self.HRauth.host() + '/HRPortal/servlet/Report?ReportName=AAA_ElencoPresenti&m_cWv=Rows%3D0%0A0%5Cu0023m_cMode%3Dhyperlink%0A0%5Cu0023outputFormat%3DCSV%0A0%5Cu0023pageFormat%3DA4%0A0%5Cu0023rotation%3DLANDSCAPE%0A0%5Cu0023marginTop%3D7%0A0%5Cu0023marginBottom%3D7%0A0%5Cu0023marginLeft%3D7%0A0%5Cu0023hideOptionPanel%3DT%0A0%5Cu0023showAfterCreate%3DTrue%0A0%5Cu0023mode%3DDOWNLOAD%0A0%5Cu0023ANQUERYFILTER%3D1%0A0%5Cu0023pRAPPORTO%3D%0A0%5Cu0023pFILIALE%3D%0A0%5Cu0023pUFFICIO%3D%0A0%5Cu0023m_cParameterSequence%3Dm_cMode%2CoutputFormat%2CpageFormat%2Crotation%2CmarginTop%2CmarginBottom%2CmarginLeft%2Cmode%2ChideOptionPanel%2CshowAfterCreate%2CANQUERYFILTER%2CpRAPPORTO%2CpFILIALE%2CpUFFICIO%0A'

        ##self.session = self.HRauth.session()
        ##if not debug:
        ##    try:
        ##        self.post = self.HRauth.post()
        ##    except:
        ##        raise ConnectionError("[HRget] *** ERROR *** connecting to portal")
        ##        sys.exit(-1)

        ##self.cookies = self.session.cookies

        ### if self.verbose > 1:
        ###    print (">>>USERNAME>>>", self.HRauth.username())
        ###    print (">>>IDEMPLOY>>>", self.HRauth.idemploy())
        ###    #print ("[{}]@{}".format(__class__.__name__, sys._getframe().f_code.co_name))
        ###    print (">>>CODE>>>", self.post.status_code)
        ###    print (">>>HISTORY>>>", self.post.history)
        ###    print (">>>HEADERS>>>", self.post.headers)
        ###    print (">>>COOKIES>>>", self.post.cookies)
        ###    print (">>>LOCATION>>>", self.post.headers['location'])
        ###    #print (">>>PAGE>>>", self.post.text)


    def get_range(self, day_range):

       data = []
       for d in day_range:
           data.append(self.get(d.year, d.month, d.day))

       return data


    def _check_data(self, d, year, month, day):
        # check data in month
        if len(d) < 1:
            raise Exception("[HRget] *** ERROR *** Data not found in month {}-{}".format(year, month))
        # check data in day
        if day:
            try:
                d[day-1]
            except:
                raise Exception("[HRget] *** ERROR *** Data not found in day {}-{}-{}".format(year, month, day))

            if day < 1:
                raise Exception("[HRget] *** ERROR *** illegal day {}".format(day))


    def get(self, year  = datetime.datetime.today().year,
                  month = datetime.datetime.today().month,
                  day   = None):

        num_days_in_month = calendar.monthrange(year, month)[1]

        last_day = num_days_in_month
        if dayutils.is_same_month( datetime.datetime(year, month, 1), datetime.datetime.today() ):
           last_day = datetime.datetime.today().day

        if day == None:
            day = datetime.datetime.today().day

        headers = {
                   'Pragma': 'no-cache',
                   'Cache-Control': 'no-cache'
                  }

        _date = f"{year}{str(month).zfill(2)}{str(day).zfill(2)}"

        if self.verbose:
            print(_date)

        params = {
                "pDATAINIZIO"         : _date,
                "pDATAFINE"           : _date,
                "pPRIMAVOLTA"         : "N",
                #"pCOLONNE"            : "Giorno#Anomalie#Anomalie Non Vincolanti#Rilevazioni#Ore Ordinarie#Giustificativi#Richieste#Piano Ferie#Orario#",
                "pCOLONNE"            : "Giorno%23Anomalie%23Anomalie%20Non%20Vincolanti%23Rilevazioni%23Ore%20Ordinarie%23Giustificativi%23Richieste%23Piano%20Ferie%23Orario%23",
                "pABILITATS"          : "N",
                "pABILNS"             : "N",
                "pTIPONS"             : "1",
                "pABILSCHE"           : "N",
                "pTACART"             : "N",
                "pIMPORTVOCI"         : "S",
                "pIGFLEX"             : "N",
                "pIGFLEXPROG"         : "N",
                "pFLEXHHMM"           : "",
                "pIGVISQTA"           : "M",
                "pDATTMI"             : "",
                "pDADRATIM"           : "S",
                "pCARORI"             : "N",
                "pNOVINCO"            : "",
                "pIGESCMTIM"          : "",
                "pDISMTIMB"           : "",
                "pINIBINSERT"         : "N",
                "pTIMBORIG"           : "N",
                "pABILVALIDCART"      : "N",
                "pLIVELLOCART"        : "0",
                "pMODIFICACARTELLINO" : "N",
                "pABILPF"             : "S",
                "pVISORECART"         : "S",
                "pABILSCHEDULING"     : "N",
                "pTURNOSCHEDULING"    : "N",
                "pFLSHOPRE0"          : "N",
                "m_cID"               : "4aed913a67dafea9c8d7a954aca98878",
                }

        self.HRauth.reset()
        p = self.HRauth.session().get(self.sheet_url, cookies=self.HRauth.cookies(), params=params)

        js = re.findall("(?:Function return value:)(.*)",p.text)[0]

        d = json.loads(js)

        if self.verbose > 2:
            print()
            for k, v in d.items():
                print(k, v)
            print()

        return d


    def totalizators(self,
                     year  = datetime.date.today().year,
                     month = datetime.date.today().month):

        date = datetime.date(year, month, 1) + datetime.timedelta(days=calendar.monthrange(year, month)[1])

        headers = {}

        params = {
                  'rows' : 100,
                  'startrow' : '0',
                  'count' : 'false',
                  'cmdhash':'2e2926382311a0b72e72cd1e1cdc4ccc',
                  'sqlcmd' : 'rows:hfpr_fgadgetconta',
                  'pIDEMPLOY': self.HRauth.idemploy(),
                  'pIDCOMPANY':'000001',
                  'pDATA':date,
                  'pADMIN':'',
                 }

        p = self.HRauth.session().post(self.sheet_url, cookies=self.HRauth.cookies())

        p = self.HRauth.session().post(self.post_url, headers=headers, cookies=self.HRauth.cookies(), params=params)

        d = p.json()['Data'][:-1]
        f = p.json()['Fields']

        json = {'Fields' : f, 'Data' : d}

        return json


    def phone(self, names = [], phones = []):

        headers = {}

        params = {
                  'rows'      : '2000',
                  'startrow'  : '0',
                  'count'     : 'true',
                  'cmdhash'   : '870a49c3706613d8026d2b84cd14150b',
                  'sqlcmd'    : 'q_rubrica',
                  'pANSURNAM' : '',
                 }

        p = self.HRauth.session().post(self.hash_url, headers=headers, cookies=self.HRauth.cookies(), params=None)

        matches = re.findall("(?<='q_rubrica',).*", p.text)

        t = re.findall("(?:\')(\w+)(?:\')", matches[0])

        token = t[5]

        params['cmdhash'] = token

        p = self.HRauth.session().post(self.portal_url, headers=headers, cookies=self.HRauth.cookies(), params=params)

        try:
           p.json()['Data'][:-1]
        except:
           return OrderedDict()

        json  = {'Fields' : p.json()['Fields'], 'Data' : p.json()['Data'][:-1]}

        return json


#{{{ deprecated
    def phone_old(self, names):

        fields_to_return = ['ANSURNAM', 'ANEMAIL', 'ANTELEF', 'ANMOBILTEL']
        data_to_return   = []

        for n in names:

            name = n.upper()

            headers = {}

            params = {
                      'rows'      : '5',
                      'startrow'  : '0',
                      'count'     : 'true',
                      'cmdhash'   : '8a0d2d1c35e16e1e2135a25505b5dd32',
                      'sqlcmd'    : 'q_rubrica',
                      'queryfilter' :"ANSURNAM like '" + name + "%'",
                      'pANSURNAM' : '',
                     }

            p = self.HRauth.session().post(self.portal_url, headers=headers, cookies=self.HRauth.cookies(), params=params)

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


    def presence_single(self, name):

        headers = {}
        params = {
                  'rows'      : '15',
                  'startrow'  : '0',
                  'count'     : 'true',
                  'cmdhash'   : '3ff43ef92f5f9df7f54c554adae919a3',
                  'sqlcmd'    : 'core_qzoomgen',
                  'queryfilter' :"DSVALUE like '{}%'".format(name.upper()),
                  'ANTABLEZOOM':"hrdd_employee00",
                  'ANIDFIELD':"IDEMPLOY",
                  'ANDSFIELD':"ANSURNAM",
                  'ANDSFIELD2':"ANNAME",
                  'IDFILTER':"",
                  'ANQUERYFILTER':"1",
                 }

        p = self.HRauth.session().post(self.portal_url, headers=headers, cookies=self.HRauth.cookies(), params=params)

        try:
            d = p.json()['Data'][:-1]
        except:
            return

        try:
            w_id = d[-1][0]
        except:
            return

        p = self.session.post(
'https://{}/HRPortal/servlet/Report?ReportName=AAA_ElencoPresenti&m_cWv=Rows%3D0%0A0%5Cu0023m_cMode%3Dhyperlink%0A0%5Cu0023outputFormat%3DCSV%0A0%5Cu0023pageFormat%3DA4%0A0%5Cu0023rotation%3DLANDSCAPE%0A0%5Cu0023marginTop%3D7%0A0%5Cu0023marginBottom%3D7%0A0%5Cu0023marginLeft%3D7%0A0%5Cu0023hideOptionPanel%3DT%0A0%5Cu0023showAfterCreate%3DTrue%0A0%5Cu0023mode%3DDOWNLOAD%0A0%5Cu0023ANQUERYFILTER%3D1%0A0%5Cu0023pRAPPORTO%3D{}%0A0%5Cu0023pFILIALE%3D%0A0%5Cu0023pUFFICIO%3D%0A0%5Cu0023m_cParameterSequence%3Dm_cMode%2CoutputFormat%2CpageFormat%2Crotation%2CmarginTop%2CmarginBottom%2CmarginLeft%2Cmode%2ChideOptionPanel%2CshowAfterCreate%2CANQUERYFILTER%2CpRAPPORTO%2CpFILIALE%2CpUFFICIO%0A'.format(self.self.HRauth.host(), w_id)
)

        csv_data = p.text

        return {'csv_data' : csv_data}


    def presence(self):

        p = self.HRauth.session().post(self.presence_url)

        csv_data = p.text

        return {'csv_data' : csv_data}


    def read(self, f):
        with open(f, 'r') as fp:
            j = json.load(fp)
        return j

    def dump(self, f, j):
        with open(f, 'w') as fp:
           json.dump(j, fp)



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


def main ():

    parser = argparse.ArgumentParser(prog='HRget',
                                     description='HR manager utility to get json data from HR portal.',
                                     formatter_class=argparse.RawTextHelpFormatter)

    add_parser(parser)

    parser.add_argument('-v', '--verbose',
                        action="count", default=0,
                        help="increase verbosity")

    parser.add_argument('-g', '--get',
                        action='store_true',
                        help="get day")

    parser.add_argument('--phone',
                        action='store_true',
                        help="get phone of workers")

    parser.add_argument('--totalizators',
                        action='store_true',
                        help="get totalizators")

    parser.add_argument('--presence',
                        action='store_true',
                        help="get presence of worker")

    parser.add_argument('--presence-single',
                        dest='presence_single',
                        help="get presence of worker")

    parser.add_argument('--dump',
                        dest='file_out',
                        help="dump to file")

    parser.add_argument('--read',
                        dest='file_input',
                        help="read from file")

    HRauth.add_parser(parser)

    args = parser.parse_args()

    djson = None


    auth = HRauth.HRauth(**vars(args))

    hr_get = HRget(auth, verbose=args.verbose)


    if args.file_input:
        djson = hr_get.read(args.file_input)


    if args.get:

        djson = hr_get.get(year=args.year, month=args.month, day=args.day)

        if args.verbose:
            for k, v in zip(djson['Fields'], djson['Data']):
                print(k, " = ", v)


    if args.totalizators:

        djson = hr_get.totalizators(year=args.year, month=args.month)

        if args.verbose:
            for d in djson['Data']:
                for k, v in zip(djson['Fields'], d):
                    print(k, " = ", v)
                print()


    if args.phone:

        djson = hr_get.phone()

        if args.verbose:
            for d in djson['Data']:
                print(" ".join(d))


    if args.presence:

        djson = hr_get.presence()

        if args.verbose:
            print(djson)


    if args.presence_single:

        djson = hr_get.presence_single(args.presence_single)

        if args.verbose:
            print(djson)


    if args.file_out:
        hr_get.dump(f, djson)



if __name__ == '__main__':
    main()

