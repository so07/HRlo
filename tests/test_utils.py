#!/usr/bin/env python3
import os
import unittest
from datetime import timedelta as dt

from HRlo import utils

class test_utils(unittest.TestCase):


    def test_utils_debug(self):
        a = utils.time_sum(['23:00:00', '23:59:59'])


    def check_result(self, function, known_values):
        for value, reference in known_values:
            result = function(value)
            self.assertEqual( result, reference )


    def test_utils_time_sum(self):

        known_values = ( (['00:00'], dt(0)),
                         (['-00:00'], dt(0)),
                         (['00:01'], dt(minutes=1)),
                         (['-00:01'], dt(minutes=-1)),
                         (['00:01', '00:41'], dt(minutes=42)),
                         (['-00:01', '-00:41'], dt(minutes=-42)),
                         (['00:01', '-00:01'], dt(minutes=0)),
                         (['-00:01', '00:01'], dt(minutes=0)),
                         (['23:59:59', '23:59:59'], dt(days=1, hours=23, minutes=59, seconds=58)),
                         #(['24:00', '01:00'], dt(hours=25)),
                       )

        self.check_result(utils.time_sum, known_values)


    def test_utils_hr2seconds(self):

        known_values = ( (0, 0),
                         (1, 3600),
                         (42, 151200),
                         (10, 36000),
                         (0.1, 360),
                         (0.5, 1800),
                         (0.654, 2354.4),
                         (987.83, 3556188),
                         (-987.83, -3556188),
                       )

        self.check_result(utils.hr2seconds, known_values)


    def test_utils_hr2time(self):

        known_values = ( (0, dt(0)),
                         (1, dt(hours=1)),
                         (42, dt(hours=42)),
                         (0.1, dt(minutes=6)),
                         (0.5, dt(minutes=30)),
                         (0.25, dt(minutes=15)),
                         (0.65, dt(minutes=39)),
                         (987.83, dt(days=41, hours=3, minutes=49, seconds=48)),
                         (-987.83, dt(days=-42, hours=20, minutes=10, seconds=12)),
                       )

        self.check_result(utils.hr2time, known_values)


if __name__ == '__main__':
    unittest.main()
