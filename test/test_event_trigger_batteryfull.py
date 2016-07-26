#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import datetime
import unittest
from solar_monitor.event.trigger import BatteryFullTrigger


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

    @unittest.skip
    def test_exec_none_w_falling_set(self, MockPopen):
        class DummyProc(object):
            pass

        # prepare test environment
        proc = DummyProc()
        proc.communicate = MagicMock(return_value=(b'', b''))
        MockPopen.return_value = proc

        battery = BatteryFullTrigger(cmd='ls', target_edge=BatteryHandler.EDGE_FALLING, threshold_voltage=12.0)

        rawdata = {}
        rawdata['at'] = datetime.now()
        rawdata['data'] = {'Battery Voltage': {'value': 12.5}}
        battery.exec(rawdata)

        rawdata['data'] = {'Battery Voltage': {'value': 12.5}}
        battery.exec(rawdata)

        # verify
        proc.communicate.assert_not_called()
        MockPopen.assert_not_called()

    @unittest.skip
    def test_exec_rising_w_falling_set(self, MockPopen):
        class DummyProc(object):
            pass

        # prepare test environment
        proc = DummyProc()
        proc.communicate = MagicMock(return_value=(b'', b''))
        MockPopen.return_value = proc

        battery = BatteryHandler(cmd='ls', target_edge=BatteryHandler.EDGE_FALLING, threshold_voltage=12.0)

        rawdata = {}
        rawdata['at'] = datetime.now()
        rawdata['data'] = {'Battery Voltage': {'value': 12.5}}
        battery.exec(rawdata)

        rawdata['data'] = {'Battery Voltage': {'value': 13.0}}
        battery.exec(rawdata)

        # verify
        proc.communicate.assert_not_called()
        MockPopen.assert_not_called()

    @unittest.skip
    def test_exec_falling_w_falling_set(self, MockPopen):
        class DummyProc(object):
            pass

        # prepare test environment
        proc = DummyProc()
        proc.communicate = MagicMock(return_value=(b'', b''))
        MockPopen.return_value = proc

        battery = BatteryHandler(cmd='ls', target_edge=BatteryHandler.EDGE_FALLING, threshold_voltage=12.0)

        rawdata = {}
        rawdata['at'] = datetime.now()
        rawdata['data'] = {'Battery Voltage': {'value': 12.5}}
        battery.exec(rawdata)

        rawdata['data'] = {'Battery Voltage': {'value': 11.5}}
        battery.exec(rawdata)

        # verify
        proc.communicate.assert_called_once_with()
        MockPopen.assert_called_once_with(['ls'], stdout=PIPE, stderr=PIPE)

    @unittest.skip
    def test_exec_none_w_rising_set(self, MockPopen):
        class DummyProc(object):
            pass

        # prepare test environment
        proc = DummyProc()
        proc.communicate = MagicMock(return_value=(b'', b''))
        MockPopen.return_value = proc

        battery = BatteryHandler(cmd='ls', target_edge=BatteryHandler.EDGE_RISING, threshold_voltage=12.0)

        rawdata = {}
        rawdata['at'] = datetime.now()
        rawdata['data'] = {'Battery Voltage': {'value': 12.5}}
        battery.exec(rawdata)

        rawdata['data'] = {'Battery Voltage': {'value': 12.5}}
        battery.exec(rawdata)

        # verify
        proc.communicate.assert_not_called()
        MockPopen.assert_not_called()

    @unittest.skip
    def test_exec_rising_w_rising_set(self, MockPopen):
        class DummyProc(object):
            pass

        # prepare test environment
        proc = DummyProc()
        proc.communicate = MagicMock(return_value=(b'', b''))
        MockPopen.return_value = proc

        battery = BatteryHandler(cmd='ls', target_edge=BatteryHandler.EDGE_RISING, threshold_voltage=12.0)

        rawdata = {}
        rawdata['at'] = datetime.now()
        rawdata['data'] = {'Battery Voltage': {'value': 12.5}}
        battery.exec(rawdata)

        rawdata['data'] = {'Battery Voltage': {'value': 13.0}}
        battery.exec(rawdata)

        # verify
        proc.communicate.assert_called_once_with()
        MockPopen.assert_called_once_with(['ls'], stdout=PIPE, stderr=PIPE)

    @unittest.skip
    def test_exec_falling_w_rising_set(self, MockPopen):
        class DummyProc(object):
            pass

        # prepare test environment
        proc = DummyProc()
        proc.communicate = MagicMock(return_value=(b'', b''))
        MockPopen.return_value = proc

        battery = BatteryHandler(cmd='ls', target_edge=BatteryHandler.EDGE_RISING, threshold_voltage=12.0)

        rawdata = {}
        rawdata['at'] = datetime.now()
        rawdata['data'] = {'Battery Voltage': {'value': 12.5}}
        battery.exec(rawdata)

        rawdata['data'] = {'Battery Voltage': {'value': 11.5}}
        battery.exec(rawdata)

        # verify
        proc.communicate.assert_not_called()
        MockPopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
