#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from solar_monitor.event.trigger import BatteryLowTrigger


class TestBatteryLowTrigger(unittest.TestCase):
    """ 親のEventListenerクラスで実施済みテスト以外をテストする """

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

    @unittest.skip
    def test_append(self):
        """  """
        pass


if __name__ == "__main__":
    unittest.main()
