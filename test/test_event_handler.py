#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from solar_monitor.event.base import IEventHandler


class TestIEventHandler(unittest.TestCase):
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
    def test_temp(self):
        eh = IEventHandler()
        eh.start()


if __name__ == "__main__":
    unittest.main()
