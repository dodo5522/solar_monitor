#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import datetime
import unittest
from solar_monitor.event.trigger import ChargeCurrentHighTrigger
from solar_monitor.event.handler import IEventHandler
from unittest.mock import MagicMock


class TestChargeCurrentHighTrigger(unittest.TestCase):
    """test ChargeCurrentHighTrigger class."""

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
        DummyEventHandler = MagicMock(spec=IEventHandler)

        event_trigger = ChargeCurrentHighTrigger(full_current=15.0)
        hoge_handler = DummyEventHandler()

        event_trigger.append(hoge_handler)
        event_trigger.start()

        expected_data = {
            "at": datetime.datetime.now().isoformat(),
            "data": {
                "Charge Current": {
                    "value": 14.0,
                    "unit": "A"
                }
            }
        }

        event_trigger.put_q(expected_data)
        event_trigger.join_q()

        event_trigger.stop()
        event_trigger.join()

        if sys.version_info[:2] >= (3, 5):
            hoge_handler.put_q.assert_not_called()
            hoge_handler.join_q.assert_not_called()
        else:
            self.assertFalse(hoge_handler.put_q.called)
            self.assertFalse(hoge_handler.join_q.called)

    def test_higher_current_than_intialized_one(self):
        DummyEventHandler = MagicMock(spec=IEventHandler)

        event_trigger = ChargeCurrentHighTrigger(full_current=15.0)
        hoge_handler = DummyEventHandler()

        event_trigger.append(hoge_handler)
        event_trigger.start()

        expected_data = {
            "at": datetime.datetime.now().isoformat(),
            "data": {
                "Charge Current": {
                    "value": 15.1,
                    "unit": "A"
                }
            }
        }

        event_trigger.put_q(expected_data)
        event_trigger.join_q()

        event_trigger.stop()
        event_trigger.join()

        self.assertEqual(hoge_handler.put_q.call_args[0][0]["at"], expected_data["at"])
        self.assertEqual(
            hoge_handler.put_q.call_args[0][0]["data"]["Charge Current"]["value"],
            expected_data["data"]["Charge Current"]["value"])

    def test_current_equals_intialized_one(self):
        DummyEventHandler = MagicMock(spec=IEventHandler)

        event_trigger = ChargeCurrentHighTrigger(full_current=15.0)
        hoge_handler = DummyEventHandler()

        event_trigger.append(hoge_handler)
        event_trigger.start()

        expected_data = {
            "at": datetime.datetime.now().isoformat(),
            "data": {
                "Charge Current": {
                    "value": 15.0,
                    "unit": "A"
                }
            }
        }

        event_trigger.put_q(expected_data)
        event_trigger.join_q()

        event_trigger.stop()
        event_trigger.join()

        self.assertEqual(hoge_handler.put_q.call_args[0][0]["at"], expected_data["at"])
        self.assertEqual(
            hoge_handler.put_q.call_args[0][0]["data"]["Charge Current"]["value"],
            expected_data["data"]["Charge Current"]["value"])

    def test_current_gets_over_intialized_one(self):
        DummyEventHandler = MagicMock(spec=IEventHandler)

        event_trigger = ChargeCurrentHighTrigger(full_current=15.0)
        hoge_handler = DummyEventHandler()

        event_trigger.append(hoge_handler)
        event_trigger.start()

        expected_data = [
            {
                "at": datetime.datetime.now().isoformat(),
                "data": {
                    "Charge Current": {
                        "value": 14.9,
                        "unit": "A"
                    }
                }
            },
            {
                "at": datetime.datetime.now().isoformat(),
                "data": {
                    "Charge Current": {
                        "value": 15.1,
                        "unit": "A"
                    }
                }
            },
        ]

        for data in expected_data:
            event_trigger.put_q(data)
            event_trigger.join_q()

        event_trigger.stop()
        event_trigger.join()

        self.assertEqual(hoge_handler.put_q.call_args[0][0]["at"], expected_data[-1]["at"])
        self.assertEqual(
            hoge_handler.put_q.call_args[0][0]["data"]["Charge Current"]["value"],
            expected_data[-1]["data"]["Charge Current"]["value"])


if __name__ == "__main__":
    unittest.main()
