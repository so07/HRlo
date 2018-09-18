#!/usr/bin/env python3
import os
import requests
import getpass
import base64

from configparser import ConfigParser

HRauth_default = {
    'config_file' : os.path.join( os.path.expanduser("~"), '.HRlo'),
    'password_encoding' : 'base64',
    'remove_config_file' : False,
    'save' : False,
    'required' : ['host', 'username', 'idemploy'],
}

class HRauth(dict):

   HRauth_config_option = 'HRauth'

   def __init__(self, **kwargs):

      dict.__init__(self, **HRauth_default)
      # update with arguments
      self.update(kwargs)

      if self['remove_config_file']:
          self._remove_config_file()

      # read from config_file
      self.update( self._read_config_file(self['config_file']) )
      # read from args
      self.update( {k: kwargs[k] for k in self['required'] if kwargs.get(k, None)} )

      self._check_required()

      if not self.get('password', False):
         self['password'] = self._encode(getpass.getpass())

      self._session = requests.Session()

      # check login to HR
      self.login()

      if self['save']:
          if self.login():
              self._write_config_file(self['config_file'])


   def _encode(self, _pass):

      if self['password_encoding'] == 'base64':
          if isinstance(_pass, bytes):
              _pass = base64.b64encode(_pass)
          else:
             _pass = base64.b64encode(_pass.encode('ascii'))
      else:
          pass

      if isinstance(_pass, bytes):
          _pass = _pass.decode()

      return _pass


   def _decode(self, _pass):

      if self['password_encoding'] == 'base64':
          _pass = base64.b64decode(_pass)
      else:
          pass

      return _pass


   def _check_required(self):
      missing = []
      for k in self['required']:
         if not self.get(k, False):
            missing.append(k)
      if missing:
         raise Exception("[HRauth] *** ERROR *** missing required args: {}".format( ", ".join(missing) ))


   def _read_config_file(self, fname):
      """Read from config file"""

      if not os.path.isfile(fname):
         return {}

      parser = ConfigParser()
      parser.read(fname)

      return {k: parser.get(self.HRauth_config_option, k) for k in parser.options(self.HRauth_config_option)}


   def _write_config_file(self, fname):
       parser = ConfigParser()

       parser.add_section(self.HRauth_config_option)

       if self.get('host', None):
          parser.set(self.HRauth_config_option, 'host', self['host'])
       if self.get('username', None):
          parser.set(self.HRauth_config_option, 'username', self['username'])
       if self.get('idemploy', None):
          parser.set(self.HRauth_config_option, 'idemploy', str(self['idemploy']))

       if self['save_password']:
          parser.set(self.HRauth_config_option, 'password', self['password'])

       with open(fname, "w") as f:
          parser.write(f)


   def _remove_config_file(self):
       if os.path.isfile(self['config_file']):
         print("Removing config file :", self['config_file'])
         os.remove(self['config_file'])


   def host(self):
       return self['host']

   def username(self):
       return self['username']

   def idemploy(self):
       return "{:0>7}".format(str(self['idemploy']))

   def login_url(self):
       return 'https://' + self.host() + '/HRPortal/servlet/cp_login'

   def login(self):
       return self._check_login(self.post())

   def _check_login(self, session):
       try:
          if 'jsp/home.jsp' in session.headers['location']:
             return True
       except:
          raise Exception("[HRauth] *** ERROR *** on HR authentication!")

   def session(self):
       return self._session

   def post(self):
       p = self.session().get(self.login_url())
       cookies = self.session().cookies.get_dict()
       cookies = "; ".join([ "{}={}".format(k, cookies[k]) for k in cookies.keys()])
       headers = {
           'Accept'                    : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Encoding'           : 'gzip, deflate, br',
           'Accept-Language'           : 'en-US,en;q=0.9',
           'Cache-Control'             : 'no-cache',
           'Connection'                : 'keep-alive',
           'Content-Type'              : 'application/x-www-form-urlencoded',
           'Cookie'                    : cookies,
           'Host'                      : self.host(),
           'Origin'                    : 'https://{}'.format(self.host()),
           'Pragma'                    : 'no-cache',
           'Referer'                   : 'https://{}/HRPortal/jsp/login.jsp'.format(self.host()),#?cpccchk=0.14902908704579954',
           'Upgrade-Insecure-Requests' : '1',
##           'User-Agent'                : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
       }
       auth = {
           'm_cUserName' : self['username'],
           'm_cPassword' : self._decode(self['password']),
           'm_cAction' : 'login',
           'w_Modal':'N',
           'wSHOWSENDMYPWD':'true',
           'mylink':'C',
           'm_cFailedLoginReason':'',
           'ssotrust':'',
           'GWINLOGON':'',
           'g_codute':'0.0',
           'm_cURL':'',
           'm_cURLOnError':'jsp/login.jsp',
           'error':'0',
           'm_cForceLogin':'',
           'w_FirstCodAzi':'000001',
           'g_UserCode':'-1',
           'g_UserName':'',
           'ssoStatus':'0',
           'm_cInstance':'',
           'm_cCaptcha':'',
           'g_codazi':'000001',
           'Nodes':'t',
           'memo':'',
           'TITOLO':'f',
           'GLOGOLGINURL':'../loghi/CIS.png',
           'ERM_GANVERATT':'070800',
           'mylang':'',
           'browserlang':'',
           'GLOGOLOGIN':'',
           'g_UserLang':'',
           'GLANGUAGEINSTALL':';DEU|deutsch|../images/flag/Germany.png;ENG|English|../images/flag/UnitedKingdom.png;FRA|francais|../images/flag/France.png;ITA|Italiano|../images/flag/Italy.png;POR|portuguese|../images/flag/Portugal.png;RON|romanian|../images/flag/default.png;SPA|espanol|../images/flag/Spain.png',
           'GFLSENDMYPWD':'S',
           'GERMNAME':'HRPortal',
           'GLOGINTITLECO':'',
           'GIDLANGUAGE':'ITA',
       }
       return self.session().post(self.login_url(), data=auth, allow_redirects=False, headers=headers)


def add_parser(parser):

   authparser = parser.add_argument_group('authentication options')

   authparser.add_argument('-u', '--username',
                           help='Username')

   authparser.add_argument('-i', '--idemploy',
                           help='ID employee')

   authparser.add_argument('-a', '--url',
                           dest='host',
                           help='HR url')

   authparser.add_argument('-c', '--config-file',
                           default=HRauth_default['config_file'],
                           help='Configuration file (default %(default)s)')

   authparser.add_argument('-s', '--save',
                           action='store_true',
                           help='Save HR authentication options in HRauth config file')

   authparser.add_argument('--save-password',
                           action='store_true',
                           help='Save HR authentication password in HRauth config file')

   authparser.add_argument('--remove-config-file',
                           action='store_true',
                           help='Remove HR config file')

   args = parser.parse_args()

   return vars(args)


def main ():

   import argparse

   parser = argparse.ArgumentParser(prog='HRauth',
                                    description='Module to authenticate on HR.',
                                    formatter_class=argparse.RawTextHelpFormatter)
   add_parser(parser)

   args = parser.parse_args()

   auth = HRauth(**vars(args))

   if auth.login():
       print("Successfully login with user: {}".format(auth.username()))


if __name__ == '__main__':
    main()

