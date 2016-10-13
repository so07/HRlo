#!/usr/bin/env python3
import os
import unittest
import datetime

from HRlo.HRauth import HRauth, HRauth_default
from HRlo.HRget import HRget

class test_HRget_inititalization(unittest.TestCase):

    config_file = HRauth_default['config_file']

    def setUp(self):
        if not os.path.isfile(self.config_file):
            raise Exception("HRauth configuration file not found in: {}".format(self.config_file))
        self.auth = HRauth( config_file=self.config_file )

    def tearDown(self):
        pass

    def test_HRget_initialization(self):
        HRget(self.auth)


class test_HRget_functionalities(unittest.TestCase):

    config_file = HRauth_default['config_file']

    def setUp(self):
        if not os.path.isfile(self.config_file):
            raise Exception("HRauth configuration file not found in: {}".format(self.config_file))
        self.auth = HRauth( config_file=self.config_file )
        self.get = HRget(self.auth)
        self.today = datetime.datetime.today()

    def tearDown(self):
        pass

    def test_HRget_get_default(self):
        default = self.get.get()

    def test_HRget_get_error_day(self):
        self.assertRaises( Exception, self.get.get, day=33 )

    def test_HRget_get_error_day2(self):
        self.assertRaises( Exception, self.get.get, day=-1 )

    def test_HRget_get_error_month(self):
        self.assertRaises( Exception, self.get.get, month=13 )

    def test_HRget_get_date(self):
        date = self.get.get(self.today.year, self.today.month, self.today.day)

    def test_HRget_get_day(self):
        day = self.get.get(day=self.today.day)

    def test_HRget_get_month(self):
        month = self.get.get(month=self.today.month)

    def test_HRget_get_year(self):
        year = self.get.get(year=self.today.year)

    #def test_HRget_get_range(self):
    #    pass

    #def test_HRget_totalizators(self):
    #    pass

    #def test_HRget_phone(self):
    #    pass

    #def test_HRget_presence(self):
    #    pass

    #def test_HRget_check_data(self):
    #    pass

    #def test_HRget_read(self):
    #    pass

    #def test_HRget_dump(self):
    #    pass


if __name__ == '__main__':
    unittest.main()
