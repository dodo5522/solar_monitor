#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import unittest
from datetime import datetime
from solar_monitor.hook.battery import BatteryHandler
from subprocess import PIPE
from unittest.mock import patch
from unittest.mock import MagicMock


class TestBatteryHandler(unittest.TestCase):
    """test BatteryHandler class."""

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

    def setUp_edge(self, first, second, target, target_edge=BatteryHandler.EDGE_FALLING):
        class _Proc(object):
            pass

        proc = _Proc()
        proc.communicate = MagicMock(return_value=(b'', b''))

        pat = patch('solar_monitor.hook.battery.subprocess.Popen', autospec=True, return_value=proc)
        popen = pat.start()
        bat = BatteryHandler(cmd='ls', target_edge=target_edge, target_volt=target)

        rawdata = {}
        rawdata['at'] = datetime.now()
        rawdata['data'] = {'Battery Voltage': {'value': first}}
        bat.exec(rawdata)

        rawdata['data']['Battery Voltage']['value'] = second
        bat.exec(rawdata)

        pat.stop()

        return (proc, popen)

    @unittest.skipIf(sys.version_info < (3, 5), "This python version doesn't support assert_not_called()")
    def test_exec_none_w_falling_set(self):
        proc, popen = self.setUp_edge(12.5, 12.5, 12.0)

        try:
            proc.communicate.assert_not_called()
            popen.assert_not_called()
        except AttributeError as _e:
            print(str(_e) + '(maybe your python3 version is less than 3.5.')

    @unittest.skipIf(sys.version_info < (3, 5), "This python version doesn't support assert_not_called()")
    def test_exec_rising_w_falling_set(self):
        proc, popen = self.setUp_edge(12.5, 13.0, 12.0)

        try:
            proc.communicate.assert_not_called()
            popen.assert_not_called()
        except AttributeError as _e:
            print(str(_e) + '(maybe your python3 version is less than 3.5.')

    def test_exec_falling_w_falling_set(self):
        proc, popen = self.setUp_edge(12.5, 11.5, 12.0)

        proc.communicate.assert_called_once_with()
        popen.assert_called_once_with(['ls'], stdout=PIPE, stderr=PIPE)

    @unittest.skipIf(sys.version_info < (3, 5), "This python version doesn't support assert_not_called()")
    def test_exec_none_w_rising_set(self):
        proc, popen = self.setUp_edge(12.5, 12.5, 12.0, target_edge=BatteryHandler.EDGE_RISING)

        try:
            proc.communicate.assert_not_called()
            popen.assert_not_called()
        except AttributeError as _e:
            print(str(_e) + '(maybe your python3 version is less than 3.5.')

    def test_exec_rising_w_rising_set(self):
        proc, popen = self.setUp_edge(12.5, 13.0, 12.0, target_edge=BatteryHandler.EDGE_RISING)

        proc.communicate.assert_called_once_with()
        popen.assert_called_once_with(['ls'], stdout=PIPE, stderr=PIPE)

    @unittest.skipIf(sys.version_info < (3, 5), "This python version doesn't support assert_not_called()")
    def test_exec_falling_w_rising_set(self):
        proc, popen = self.setUp_edge(12.5, 11.5, 12.0, target_edge=BatteryHandler.EDGE_RISING)

        try:
            proc.communicate.assert_not_called()
            popen.assert_not_called()
        except AttributeError as _e:
            print(str(_e) + '(maybe your python3 version is less than 3.5.')


if __name__ == "__main__":
    unittest.main()
