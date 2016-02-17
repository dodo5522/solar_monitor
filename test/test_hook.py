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

    def test_exec_falling(self):
        class _Proc(object):
            pass

        proc = _Proc()
        proc.communicate = MagicMock(return_value=(b'', b''))

        _p = patch('solar_monitor.hook.battery.subprocess.Popen', autospec=True, return_value=proc)
        _m = _p.start()
        bat = BatteryHandler(cmd='ls', target_edge=BatteryHandler.EDGE_FALLING, target_volt=12.0)

        rawdata = {}
        rawdata['at'] = datetime.now()
        rawdata['data'] = {'Battery Voltage': {'value': 12.5}}
        bat.exec(rawdata)

        rawdata['data']['Battery Voltage']['value'] = 11.5
        bat.exec(rawdata)

        _p.stop()

        proc.communicate.assert_called_once_with()
        _m.assert_called_once_with(['ls'], stdout=PIPE, stderr=PIPE)

if __name__ == "__main__":
    unittest.main()
