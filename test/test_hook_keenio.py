#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from datetime import datetime
from solar_monitor.hook.keenio import KeenIoHandler
from unittest.mock import patch
from unittest.mock import MagicMock


class TestKeenioHandler(unittest.TestCase):
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

    def test_exec_(self):
        class _DummyKeenClient(object):
            pass

        kc = _DummyKeenClient()
        kc.add_events = MagicMock(return_value=None)

        kc_patch = patch('solar_monitor.hook.keenio.KeenClient', autospec=True, return_value=kc)
        mock_kc = kc_patch.start()

        dummy_project_id = 'dummy_project_id'
        dummy_write_key = 'dummy_write_key'
        kh = KeenIoHandler(dummy_project_id, dummy_write_key)

        args = {}
        args['source'] = 'solar'
        args['at'] = datetime.now()
        args['data'] = {
            'Array Current': {'group': 'Array', 'unit': 'A', 'value': 1.4},
            'Array Voltage': {'group': 'Array', 'unit': 'V', 'value': 53.41}}

        kh.exec(args)

        kc_patch.stop()

        mock_kc.assert_called_once_with(project_id=dummy_project_id, write_key=dummy_write_key)

        self.maxDiff = None
        self.assertEqual(kc.add_events.call_count, 1)
        self.assertEqual(kc.add_events.call_args[0][0], {
            'offgrid': [
                {'value': 1.4, 'unit': 'A', 'group': 'Array', 'source': 'solar', 'keen': {'timestamp': args['at'].isoformat() + 'Z'}, 'label': 'Array Current'},
                {'value': 53.41, 'unit': 'V', 'group': 'Array', 'source': 'solar', 'keen': {'timestamp': args['at'].isoformat() + 'Z'}, 'label': 'Array Voltage'}
            ]
        })

if __name__ == "__main__":
    unittest.main()
