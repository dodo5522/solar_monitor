#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import unittest
import datetime
from solar_monitor.event.trigger import BatteryLowTrigger
from unittest.mock import MagicMock


class TestBatteryLowTrigger(unittest.TestCase):
    """ 親のEventListenerクラスで実施済みテスト以外をテストする """

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

    def test_not_in_condition(self):
        """  """
        batlow_trigger = BatteryLowTrigger(lowest_voltage=12.0)
        batlow_trigger.run_in_condition_ = MagicMock(spec=lambda x: None)
        batlow_trigger.start()

        expected_data = {
            "at": datetime.datetime.now().isoformat(),
            "data": {
                "Battery Voltage": {
                    "value": 13.0,
                    "unit": "V"
                }
            }
        }

        batlow_trigger.put_q(expected_data)
        batlow_trigger.stop()
        batlow_trigger.join()

        if sys.version_info[:2] >= (3, 5):
            batlow_trigger.run_in_condition_.assert_not_called()
        else:
            self.assertFalse(batlow_trigger.run_in_condition_.called)

    def test_low_voltage_from_first_time(self):
        """  """
        batlow_trigger = BatteryLowTrigger(lowest_voltage=12.0)
        batlow_trigger.run_in_condition_ = MagicMock(spec=lambda x: None)
        batlow_trigger.start()

        expected_data = {
            "at": datetime.datetime.now().isoformat(),
            "data": {
                "Battery Voltage": {
                    "value": 11.0,
                    "unit": "V"
                }
            }
        }

        batlow_trigger.put_q(expected_data)
        batlow_trigger.stop()
        batlow_trigger.join()

        args, _ = batlow_trigger.run_in_condition_.call_args
        got_data = args[0]

        self.assertEqual(expected_data["at"], got_data["at"])
        self.assertEqual(expected_data["data"]["Battery Voltage"]["value"], got_data["data"]["Battery Voltage"]["value"])

    def test_low_voltage_more_than_2times(self):
        """ 閾値を２回以上下回っても、トリガーを発火するのは最初の１回のみ """
        batlow_trigger = BatteryLowTrigger(lowest_voltage=12.0)
        batlow_trigger.run_in_condition_ = MagicMock(spec=lambda x: None)
        batlow_trigger.start()

        first_data = {
            "at": datetime.datetime.now().isoformat(),
            "data": {
                "Battery Voltage": {
                    "value": 12.0,
                    "unit": "V"
                }
            }
        }
        second_data = {
            "at": datetime.datetime.now().isoformat(),
            "data": {
                "Battery Voltage": {
                    "value": 11.9,
                    "unit": "V"
                }
            }
        }
        third_data = {
            "at": datetime.datetime.now().isoformat(),
            "data": {
                "Battery Voltage": {
                    "value": 11.8,
                    "unit": "V"
                }
            }
        }

        batlow_trigger.put_q(first_data)
        batlow_trigger.put_q(second_data)
        batlow_trigger.put_q(third_data)
        batlow_trigger.stop()
        batlow_trigger.join()

        args, _ = batlow_trigger.run_in_condition_.call_args
        got_data = args[0]

        self.assertEqual(second_data["at"], got_data["at"])
        self.assertEqual(second_data["data"]["Battery Voltage"]["value"], got_data["data"]["Battery Voltage"]["value"])

if __name__ == "__main__":
    unittest.main()
