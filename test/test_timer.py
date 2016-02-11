#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Test cases for timer.py module."""

import unittest
import threading
from pympler import muppy
from pympler import summary
from solar_monitor import timer


class TestTimer(unittest.TestCase):
    """Test cases for timer.py module."""

    @classmethod
    def setUpClass(cls):
        cls.event = threading.Event()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.counter = 0

    def tearDown(self):
        pass

    def dummy_main(self, **kwargs):
        max_loop = kwargs.get('max_loop')
        print("counter:" + str(self.counter))
        if self.counter >= max_loop:
            self.event.set()
        else:
            self.counter += 1

    def test_start_twice(self):
        rtimer = timer.RecursiveTimer(2, lambda x: x)

        rtimer.start()
        self.assertRaises(timer.AlreadyRunningError, rtimer.start)
        rtimer.cancel()

    def fixture_loop(self, max_loop=10):
        self.event.clear()
        interval_sec = 1

        _sum = summary.summarize(muppy.get_objects())

        rtimer = timer.RecursiveTimer(interval_sec, self.dummy_main, max_loop=max_loop)
        rtimer.start()
        res = self.event.wait(max_loop * interval_sec + 2)
        rtimer.cancel()

        _diff = summary.get_diff(_sum, summary.summarize(muppy.get_objects()))
        summary.print_(_diff)

        self.assertTrue(res)
        self.assertEqual(self.counter, max_loop)
        self.assertFalse(rtimer.is_alive())

    def test_short_loop(self):
        self.fixture_loop(10)

    def test_long_loop(self):
        self.fixture_loop(30)

if __name__ == "__main__":
    unittest.main()
