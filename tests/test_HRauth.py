#!/usr/bin/env python3
import os
import unittest

from HRlo.HRauth import HRauth, HRauth_default

class test_HRauth(unittest.TestCase):

    config_file = HRauth_default['config_file']

    def setUp(self):
        if not os.path.isfile(self.config_file):
            raise Exception("HRauth configuration file not found in: {}".format(self.config_file))

    def tearDown(self):
        pass

    def test_HRauth_definition(self):
        HRauth( config_file=self.config_file )

    def test_HRauth_login(self):
        auth = HRauth( config_file=self.config_file )
        self.assertTrue( auth.login() )


class test_HRauth_funcionalities(unittest.TestCase):

    config_file = HRauth_default['config_file']

    def setUp(self):
        if not os.path.isfile(self.config_file):
            raise Exception("HRauth configuration file not found in: {}".format(self.config_file))
        self.auth = HRauth( config_file=self.config_file )

        try:
            self.auth.login()
        except:
            raise Exception("Provide a username with a successfully login for unit tests of HRauth")

    def tearDown(self):
        pass

    def test_HRauth_host(self):
        self.auth.host()

    def test_HRauth_username(self):
        self.auth.username()

    def test_HRauth_idemploy(self):
        self.auth.idemploy()

    def test_HRauth_login_url(self):
        self.auth.login_url()

    def test_HRauth_login(self):
        self.assertTrue(self.auth.login())

    def test_HRauth_check_login(self):
        self.assertTrue(self.auth._check_login(self.auth.post()))

    def test_HRauth_session(self):
        self.auth.session()

    def test_HRauth_post(self):
        self.auth.post()


if __name__ == '__main__':
    unittest.main()
