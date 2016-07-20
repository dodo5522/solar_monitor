#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Test cases for timer.py module."""

import inspect
import sys
import threading
import unittest

from datetime import datetime
from solar_monitor import timer


class MainLoop(object):
    def __init__(self, main_id="", max_count=0):
        self.main_id_ = main_id
        self.max_count_ = max_count
        self.counter_ = 0
        self.event_ = threading.Event()  # default: False

    def main(self, **kwargs):
        self.counter_ += 1
        print("{}: counter: {}".format(self.main_id_, str(self.counter_)))

        if self.counter_ >= self.max_count_:
            self.event_.set()

    def wait(self, timeout):
        return self.event_.wait(timeout)

    def get_counter(self):
        return self.counter_


class TestTimer(unittest.TestCase):
    """Test cases for timer.py module."""

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

    def test_cancel_with_not_started(self):
        rt = timer.RecursiveTimer(1, lambda x: x)

        if sys.version_info[:2] >= (3, 1):
            with self.assertRaises(timer.NotStartedYetError):
                rt.cancel()

    def test_start_twice(self):
        rtimer = timer.RecursiveTimer(2, lambda x: x)

        if sys.version_info[:2] >= (3, 1):
            with self.assertRaises(timer.AlreadyRunningError):
                rtimer.start()
                rtimer.start()

            rtimer.cancel()

    def test_short_loop(self):
        max_count = 5
        main_loop = MainLoop(
            main_id=inspect.getframeinfo(inspect.currentframe())[2],
            max_count=max_count)

        interval_sec = 1
        rtimer = timer.RecursiveTimer(
            interval_sec,
            main_loop.main,
            max_loop=max_count)

        rtimer.start()
        time_start = datetime.now()
        res = main_loop.wait(max_count * interval_sec + 2)
        time_end = datetime.now()
        rtimer.cancel()

        print("start:" + str(time_start))
        print("end:" + str(time_end))

        self.assertGreaterEqual((time_end - time_start).seconds, max_count * interval_sec)
        self.assertLessEqual((time_end - time_start).seconds, max_count * interval_sec + 2)
        self.assertTrue(res)
        self.assertEqual(main_loop.get_counter(), max_count)
        self.assertFalse(rtimer.is_alive())

    def test_long_loop1(self):
        max_count = 10
        main_loop = MainLoop(
            main_id=inspect.getframeinfo(inspect.currentframe())[2],
            max_count=max_count)

        interval_sec = 2
        rtimer = timer.RecursiveTimer(
            interval_sec,
            main_loop.main,
            max_loop=max_count)

        rtimer.start()
        time_start = datetime.now()
        res = main_loop.wait(max_count * interval_sec + 2)
        time_end = datetime.now()
        rtimer.cancel()

        print("start:" + str(time_start))
        print("end:" + str(time_end))

        self.assertGreaterEqual((time_end - time_start).seconds, max_count * interval_sec)
        self.assertLessEqual((time_end - time_start).seconds, max_count * interval_sec + 2)
        self.assertTrue(res)
        self.assertEqual(main_loop.get_counter(), max_count)
        self.assertFalse(rtimer.is_alive())

    def test_long_loop2(self):
        max_count = 4
        main_loop = MainLoop(
            main_id=inspect.getframeinfo(inspect.currentframe())[2],
            max_count=max_count)

        interval_sec = 5
        rtimer = timer.RecursiveTimer(
            interval_sec,
            main_loop.main,
            max_loop=max_count)

        rtimer.start()
        time_start = datetime.now()
        res = main_loop.wait(max_count * interval_sec + 2)
        time_end = datetime.now()
        rtimer.cancel()

        print("start:" + str(time_start))
        print("end:" + str(time_end))

        self.assertGreaterEqual((time_end - time_start).seconds, max_count * interval_sec)
        self.assertLessEqual((time_end - time_start).seconds, max_count * interval_sec + 2)
        self.assertTrue(res)
        self.assertEqual(main_loop.get_counter(), max_count)
        self.assertFalse(rtimer.is_alive())


if __name__ == "__main__":
    unittest.main()
