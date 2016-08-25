#!/usr/bin/env python3
import os
import unittest
import datetime

from HRlo.HRauth import HRauth, HRauth_default
from HRlo.HRget import HRget
from HRlo.HRpresence import HRpresence

class test_HRpresence_inititalization(unittest.TestCase):

    config_file = HRauth_default['config_file']

    def setUp(self):
        if not os.path.isfile(self.config_file):
            raise Exception("HRauth configuration file not found in: {}".format(self.config_file))
        self.auth = HRauth( config_file=self.config_file )
        self.get = HRget(self.auth)

    def tearDown(self):
        pass

    def test_HRpresence_initialization(self):
        d = HRpresence( self.get.presence() )


class test_HRpresence_functionalities(unittest.TestCase):

    config_file = HRauth_default['config_file']

    def __init__(self, *args, **kwargs):
        super(test_HRpresence_functionalities, self).__init__(*args, **kwargs)
        if not os.path.isfile(self.config_file):
            raise Exception("HRauth configuration file not found in: {}".format(self.config_file))
        self.auth = HRauth( config_file=self.config_file )
        self.get = HRget(self.auth)
        self.presence = HRpresence( self.get.presence() )
        self.file_name = 'test_HRpresence_file'

    def test_HRpresence_len(self):
        self.assertTrue(len(self.presence))

    def test_HRpresence_dump_csv(self):
        self.presence.dump_csv(self.file_name)
        self.assertTrue( os.path.isfile(self.file_name) )
        os.remove(self.file_name)

    def test_HRpresence_dump_json(self):
        self.presence.dump_json(self.file_name)
        self.assertTrue( os.path.isfile(self.file_name) )
        os.remove(self.file_name)

    def test_HRpresence_read_csv(self):
        self.presence.dump_csv(self.file_name)
        self.assertTrue( os.path.isfile(self.file_name) )
        self.assertTrue( self.presence.read_csv(self.file_name) )
        os.remove(self.file_name)

    def test_HRpresence_read_json(self):
        self.presence.dump_json(self.file_name)
        self.assertTrue( os.path.isfile(self.file_name) )
        self.assertTrue( self.presence.read_json(self.file_name) )
        os.remove(self.file_name)


if __name__ == '__main__':
    unittest.main()
