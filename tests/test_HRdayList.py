#!/usr/bin/env python3
import os
import unittest
import datetime

from HRlo.HRauth import HRauth, HRauth_default
from HRlo.HRget import HRget
from HRlo.HRday import HRday
from HRlo.HRdayList import HRdayList

class test_HRdayList_inititalization(unittest.TestCase):

    config_file = HRauth_default['config_file']

    def setUp(self):
        if not os.path.isfile(self.config_file):
            raise Exception("HRauth configuration file not found in: {}".format(self.config_file))
        self.auth = HRauth( config_file=self.config_file )

    def tearDown(self):
        pass

    def test_HRday_initialization(self):
        HRdayList()

    def test_HRday_str(self):
        HRdayList().__str__()

    def test_HRday_repr(self):
        HRdayList().__repr__()


class test_HRdayList_functionalities(unittest.TestCase):

    config_file = HRauth_default['config_file']

    def setUp(self):
        if not os.path.isfile(self.config_file):
            raise Exception("HRauth configuration file not found in: {}".format(self.config_file))
        self.auth = HRauth( config_file=self.config_file )
        self.json = HRget(self.auth).get(day=datetime.datetime.today().day)
        self.day = HRday(self.json)
        self.daylist = HRdayList()
        self.daylist.append(self.day)

    def tearDown(self):
        pass

    def test_HRday_str(self):
        self.daylist.__str__()

    def test_HRday_repr(self):
        self.daylist.__repr__()

    def test_HRday_append(self):
        self.daylist.append(self.day)

    def test_HRday_working_days_number(self):
        self.daylist.working_days_number()

    def test_HRday_working_days_list(self):
        self.daylist.working_days_list()

    def test_HRday_is_working_list(self):
        self.daylist.is_working_list()

    def test_HRday_uptime(self):
        self.daylist.uptime()

    def test_HRday_uptime_list(self):
        self.daylist.uptime_list()

    def test_HRday_uptime_mean(self):
        self.daylist.mean(self.daylist.uptime())

    def test_HRday_anomaly(self):
        self.daylist.anomaly()

    def test_HRday_anomaly_list(self):
        self.daylist.anomaly_list()

    def test_HRday_anomaly_mean(self):
        self.daylist.mean(self.daylist.anomaly())

    def test_HRday__getattr_from_HRday_uptime(self):
        self.daylist._getattr_from_HRday('uptime')

    def test_HRday__getattr_from_HRday_anomaly(self):
        self.daylist._getattr_from_HRday('anomaly')

    def test_HRday__getattr_from_HRday_is_working(self):
        self.daylist._getattr_from_HRday('is_working')



if __name__ == '__main__':
    unittest.main()
