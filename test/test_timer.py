#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Test cases for timer.py module."""

import unittest
import threading
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

    def test_short_loop(self):
        self.event.clear()
        interval_sec = 1
        max_loop = 10

        rtimer = timer.RecursiveTimer(interval_sec, self.dummy_main, max_loop=10)
        rtimer.start()

        self.assertTrue(rtimer.is_alive())

        res = self.event.wait(max_loop * interval_sec + 2)

        self.assertTrue(res)
        self.assertEqual(self.counter, max_loop)

        rtimer.cancel()

        self.assertFalse(rtimer.is_alive())


if __name__ == "__main__":
    unittest.main()
