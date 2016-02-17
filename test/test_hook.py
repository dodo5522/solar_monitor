#!/usr/bin/env python3
# -*- coding:utf-8 -*-

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

    def set_fixture_edge(self, first, second, target):
        class _Proc(object):
            pass

        proc = _Proc()
        proc.communicate = MagicMock(return_value=(b'', b''))

        pat = patch('solar_monitor.hook.battery.subprocess.Popen', autospec=True, return_value=proc)
        popen = pat.start()
        bat = BatteryHandler(cmd='ls', target_edge=BatteryHandler.EDGE_FALLING, target_volt=target)

        rawdata = {}
        rawdata['at'] = datetime.now()
        rawdata['data'] = {'Battery Voltage': {'value': first}}
        bat.exec(rawdata)

        rawdata['data']['Battery Voltage']['value'] = second
        bat.exec(rawdata)

        pat.stop()

        return (proc, popen)

    def test_exec_none(self):
        proc, popen = self.set_fixture_edge(12.5, 12.5, 12.0)

        proc.communicate.assert_not_called()
        popen.assert_not_called()

    def test_exec_falling(self):
        proc, popen = self.set_fixture_edge(12.5, 11.5, 12.0)

        proc.communicate.assert_called_once_with()
        popen.assert_called_once_with(['ls'], stdout=PIPE, stderr=PIPE)

if __name__ == "__main__":
    unittest.main()
