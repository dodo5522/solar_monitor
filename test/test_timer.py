#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Test cases for timer.py module."""

import unittest
import threading

from datetime import datetime
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
        self.counter += 1
        print("counter:" + str(self.counter))

        if self.counter >= kwargs.get('max_loop'):
            self.event.set()

    def test_start_twice(self):
        rtimer = timer.RecursiveTimer(2, lambda x: x)

        rtimer.start()
        self.assertRaises(timer.AlreadyRunningError, rtimer.start)
        rtimer.cancel()

    def fixture_loop(self, interval_sec=1, max_loop=10):
        self.event.clear()

        rtimer = timer.RecursiveTimer(interval_sec, self.dummy_main, max_loop=max_loop)
        rtimer.start()
        time_start = datetime.now()
        res = self.event.wait(max_loop * interval_sec + 2)
        time_end = datetime.now()
        rtimer.cancel()

        print("start:" + str(time_start))
        print("end:" + str(time_end))

        self.assertGreaterEqual((time_end - time_start).seconds, max_loop * interval_sec)
        self.assertLessEqual((time_end - time_start).seconds, max_loop * interval_sec + 2)
        self.assertTrue(res)
        self.assertEqual(self.counter, max_loop)
        self.assertFalse(rtimer.is_alive())

    def test_short_loop(self):
        self.fixture_loop(1, 5)

    def test_long_loop1(self):
        self.fixture_loop(2, 10)

    def test_long_loop2(self):
        self.fixture_loop(5, 4)

if __name__ == "__main__":
    unittest.main()
