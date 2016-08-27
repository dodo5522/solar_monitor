#!/usr/bin/env python
# -*- coding:utf-8 -*-

#   Copyright 2016 Takashi Ando - http://blog.rinka-blossom.com/
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import unittest
from solar_monitor import argparser


class TestArgParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_default_args(self):
        parsed = argparser.init([])

        self.assertEqual("192.168.1.20", parsed.host_name)
        self.assertEqual(None, parsed.xively_api_key)
        self.assertEqual(None, parsed.xively_feed_key)
        self.assertEqual(None, parsed.keenio_project_id)
        self.assertEqual(None, parsed.keenio_write_key)
        self.assertEqual(None, parsed.twitter_consumer_key)
        self.assertEqual(None, parsed.twitter_consumer_secret)
        self.assertEqual(None, parsed.twitter_key)
        self.assertEqual(None, parsed.twitter_secret)
        self.assertEqual(False, parsed.battery_monitor_enabled)
        self.assertEqual(11.5, parsed.battery_limit)
        self.assertEqual("/usr/local/bin/remote_shutdown.sh", parsed.battery_limit_hook_script)
        self.assertEqual(30.0, parsed.charge_current_high)
        self.assertEqual(14.0, parsed.battery_full_limit)
        self.assertEqual(300, parsed.interval)
        self.assertEqual(None, parsed.log_file)
        self.assertEqual(False, parsed.just_get_status)
        self.assertEqual(True, parsed.status_all)
        self.assertEqual(False, parsed.debug)

    def test_first_args(self):
        argparser.init([])


if __name__ == "__main__":
    unittest.main()
