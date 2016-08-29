#!/usr/bin/env python3
import os
import unittest
import datetime

from HRlo.HRauth import HRauth, HRauth_default
from HRlo.HRget import HRget
from HRlo.HRday import HRday

class test_HRday_inititalization(unittest.TestCase):

    config_file = HRauth_default['config_file']

    def setUp(self):
        if not os.path.isfile(self.config_file):
            raise Exception("HRauth configuration file not found in: {}".format(self.config_file))
        self.auth = HRauth( config_file=self.config_file )
        self.get = HRget(self.auth)
        self.today = datetime.datetime.today()

    def tearDown(self):
        pass

    def test_HRday_initialization(self):
        json = self.get.get(day=self.today.day)
        d = HRday(json)


class test_HRget_functionalities(unittest.TestCase):

    config_file = HRauth_default['config_file']

    def setUp(self):
        if not os.path.isfile(self.config_file):
            raise Exception("HRauth configuration file not found in: {}".format(self.config_file))
        self.auth = HRauth( config_file=self.config_file )
        self.json = HRget(self.auth).get(day=datetime.datetime.today().day)
        self.day = HRday(self.json)

    def tearDown(self):
        pass

    def test_HRday_str(self):
        x = self.day.__str__()

    def test_HRday_repr(self):
        x = self.day.__repr__()

    def test_HRday_is_today(self):
        self.assertTrue(self.day.is_today())

    def test_HRday_mission(self):
        x = self.day.mission()

    def test_HRday_lunch(self):
        x = self.day.lunch()

    def test_HRday_working(self):
        x = self.day.working()

    def test_HRday_holiday(self):
        x = self.day.holiday()

    def test_HRday_rol_total(self):
        x = self.day.rol_total()

    def test_HRday_anomaly(self):
        x = self.day.anomaly()

    def test_HRday_timenet(self):
        x = self.day.timenet()

    def test_HRday_time_to_work(self):
        x = self.day.time_to_work()

    def test_HRday_remains(self):
        x = self.day.timenet()

    def test_HRday_exit(self):
        x = self.day.exit()

    def test_HRday__get_timenet(self):
        x = self.day._get_timenet()

    def test_HRday__get_hr_work_time(self):
        x = self.day._get_hr_work_time()

    def test_HRday__get_hr_real_work_time(self):
        x = self.day._get_hr_real_work_time()

    def test_HRday__get_hr_times(self):
        x = self.day._get_hr_times()

    def test_HRday__get_lunch_time(self):
        x = self.day._get_lunch_time()

    def test_HRday__get_ko_time(self):
        x = self.day._get_ko_time()

    def test_HRday__get_lunch_time_remain(self):
        x = self.day._get_lunch_time_remain()


if __name__ == '__main__':
    unittest.main()
