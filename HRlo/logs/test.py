#!/usr/bin/env python3
import unittest
import datetime
from daylog import DayLog

class test_day_null(unittest.TestCase):

   day_null = DayLog()

   def test_none(self):
      self.assertFalse(str(self.day_null))


class test_daylog_uptime(unittest.TestCase):

   knownValues = (
      (DayLog(datetime.datetime.today(), ['09:03', '10:13']), datetime.timedelta(0, 4200)),
         )

   def test_uptime(self):
      d1 = DayLog(datetime.datetime.today(), ['09:03', '10:13'])
      self.assertEqual(d1.uptime(), datetime.timedelta(0, 4200))

   def test_known_uptime(self):
      for daylog, uptime in self.knownValues: 
         self.assertEqual( daylog.uptime(), uptime )


if __name__ == '__main__':
   unittest.main()
