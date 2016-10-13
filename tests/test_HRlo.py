#!/usr/bin/env python3
import os
import unittest
import datetime

from HRlo.HRauth import HRauth, HRauth_default
from HRlo.HRget import HRget
from HRlo.HRlo import HRlo

class test_HRlo_inititalization(unittest.TestCase):

    config_file = HRauth_default['config_file']

    def setUp(self):
        if not os.path.isfile(self.config_file):
            raise Exception("HRauth configuration file not found in: {}".format(self.config_file))
        self.auth = HRauth( config_file=self.config_file )
        self.get = HRget(self.auth)

    def tearDown(self):
        pass

    def test_HRday_initialization(self):
        HRlo(self.auth)


class test_HRlo_functionalities(unittest.TestCase):

    config_file = HRauth_default['config_file']

    def __init__(self, *args, **kwarg):
        super(test_HRlo_functionalities, self).__init__(*args, **kwarg)
        if not os.path.isfile(self.config_file):
            raise Exception("HRauth configuration file not found in: {}".format(self.config_file))
        self.auth = HRauth( config_file=self.config_file )
        self.hrlo = HRlo(self.auth)

    def tearDown(self):
        pass

    def test_HRlo_str(self):
        x = self.hrlo.__str__()

    def test_HRlo_repr(self):
        x = self.hrlo.__repr__()

    def test_HRlo_day(self):
        self.hrlo.day()

#    def test_HRlo_day_today(self):
#        self.hrlo.day(datetime.datetime.today())

    def test_HRlo_week(self):
        self.hrlo.week()

    def test_HRlo_week_today(self):
        self.hrlo.week(datetime.datetime.today())

    def test_HRlo_month(self):
        self.hrlo.month()

    def test_HRlo_month_today(self):
        self.hrlo.month(datetime.datetime.today())

    def test_HRlo_report_day(self):
        self.hrlo.report_day()

#    def test_HRlo_report_day_today(self):
#        self.hrlo.report_day(datetime.datetime.today())

    def test_HRlo_report_week(self):
        self.hrlo.report_week()

    def test_HRlo_report_week_today(self):
        self.hrlo.report_week(datetime.datetime.today())

    def test_HRlo_report_month(self):
        self.hrlo.report_month()

    def test_HRlo_report_month_today(self):
        self.hrlo.report_month(datetime.datetime.today())

    def test_HRlo_anomalies(self):
        self.hrlo.anomalies()

    def test_HRlo_phone_names_empty(self):
        self.hrlo.phone(names=[])

    def test_HRlo_phone_names_none(self):
        self.hrlo.phone(names=['strange_name_1', 'strange_name_2'])

    def test_HRlo_phone_phones_empty(self):
        self.hrlo.phone(phones=[])

    def test_HRlo_phone_phones_none(self):
        self.hrlo.phone(phones=['123456789', '987654321'])

    def test_HRlo_presence_empty(self):
        self.hrlo.presence('')

    def test_HRlo_presence_none_name(self):
        self.hrlo.presence('strange_name_1')

    def test_HRlo_presence_none_list(self):
        self.hrlo.presence(['strange_name_1', 'strange_name_2'])

    def test_HRlo_totalizator_empty(self):
        self.hrlo.totalizator()

    def test_HRlo_totalizator_key(self):
        self.hrlo.totalizator('HRPY')


if __name__ == '__main__':
    unittest.main()

