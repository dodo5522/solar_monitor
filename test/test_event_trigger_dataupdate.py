#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from solar_monitor.event.trigger import DataIsUpdatedTrigger


class TestDataIsUpdatedTrigger(unittest.TestCase):
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

    def test_is_condition_always_true(self):
        trigger = DataIsUpdatedTrigger()

        self.assertTrue(trigger._is_condition(None))


if __name__ == "__main__":
    unittest.main()
