#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from datetime import datetime
from solar_monitor.event.handler import KeenIoEventHandler
from unittest.mock import patch
from unittest.mock import MagicMock


class TestKeenioEventHandler(unittest.TestCase):
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

    @patch("solar_monitor.event.handler.KeenClient", autospec=True)
    def test_post_data_to_keenio(self, mocked_client):
        client = MagicMock()
        client.add_events = MagicMock(return_value=None)
        mocked_client.return_value = client

        keen_handler = KeenIoEventHandler(
            project_id='dummy_project_id',
            write_key='dummy_write_key')

        data = {}
        data['source'] = 'solar'
        data['at'] = datetime.now()
        data['data'] = {
            'Array Current': {'group': 'Array', 'unit': 'A', 'value': 1.0},
            'Array Voltage': {'group': 'Array', 'unit': 'V', 'value': 50.0}}

        keen_handler.start()
        keen_handler.put_q(data)
        keen_handler.join_q()
        keen_handler.stop()
        keen_handler.join()

        self.assertTrue(client.add_events.called)

        for items in client.add_events.call_args[0][0]['offgrid']:
            self.assertIn('keen', items)
            items.pop('keen')
            self.assertEqual('solar', items['source'])
            items.pop('source')

        for items in client.add_events.call_args[0][0]['offgrid']:
            label = items.pop('label')
            self.assertEqual(set(data['data'][label].items()), set(items.items()))


if __name__ == "__main__":
    unittest.main()
