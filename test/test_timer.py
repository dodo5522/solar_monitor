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
        self.max_loop = 0

    def tearDown(self):
        pass

    def dummy_main(self, arg):
        if self.counter >= self.max_loop:
            self.event.set()
        else:
            self.counter += 1
            print("counter:" + str(self.counter))

    def test_start_twice(self):
        rtimer = timer.RecursiveTimer(lambda x: x, None, 2)

        rtimer.start()
        self.assertRaises(timer.AlreadyRunningError, rtimer.start)
        rtimer.cancel()

    def test_loop(self):
        self.event.clear()
        self.max_loop = 30
        interval_sec = 1

        rtimer = timer.RecursiveTimer(self.dummy_main, None, interval_sec)
        rtimer.start()

        self.assertTrue(rtimer.is_alive())

        res = self.event.wait(self.max_loop * interval_sec + 2)

        self.assertTrue(res)
        self.assertEqual(self.counter, self.max_loop)

        rtimer.cancel()

        self.assertFalse(rtimer.is_alive())


if __name__ == "__main__":
    unittest.main()
