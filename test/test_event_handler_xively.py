#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from datetime import datetime
from solar_monitor.event.handler import XivelyEventHandler
from unittest.mock import call
from unittest.mock import patch
from unittest.mock import MagicMock


class TestXivelyEventHandler(unittest.TestCase):
    """test KeenIoHandler class."""

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

    @patch("solar_monitor.event.handler.xively.Datastream", autospec=True)
    @patch("solar_monitor.event.handler.xively.XivelyAPIClient", autospec=True)
    def test_post_data_to_xively(self, mocked_api_client, mocked_datastream):
        client = MagicMock()
        client.update = MagicMock(return_value=None)
        api = MagicMock()
        api.feeds = MagicMock()
        api.feeds.get = MagicMock(return_value=client)
        mocked_api_client.return_value = api

        xively_handler = XivelyEventHandler(
            api_key="dummy",
            feed_key="dummy")

        data = {}
        data['source'] = 'solar'
        data['at'] = datetime.now()
        data['data'] = {
            'Array Current': {'group': 'Array', 'unit': 'A', 'value': 1.4},
            'Array Voltage': {'group': 'Array', 'unit': 'V', 'value': 53.41}}

        xively_handler.start()
        xively_handler.put_q(data)
        xively_handler.join_q()
        xively_handler.stop()
        xively_handler.join()

        api.feeds.get.assert_called_once_with("dummy")

        calls = [
            call(id="ArrayCurrent", current_value=1.4, at=data["at"]),
            call(id="ArrayVoltage", current_value=53.41, at=data["at"]),
        ]
        mocked_datastream.assert_has_calls(calls, any_order=True)

        self.assertEqual(2, len(client.datastreams))
        client.update.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
