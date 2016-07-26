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

    @unittest.skip
    def test_exec(self):
        class _DummyKeenClient(object):
            pass

        # 差分表示の上限をなくす
        self.maxDiff = None

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
        self.assertEqual(kc.add_events.call_count, 1)

        for items in kc.add_events.call_args[0][0]['offgrid']:
            self.assertIn('keen', items)
            items.pop('keen')
            self.assertEqual('solar', items['source'])
            items.pop('source')

        for items in kc.add_events.call_args[0][0]['offgrid']:
            label = items.pop('label')
            self.assertEqual(set(args['data'][label].items()), set(items.items()))


if __name__ == "__main__":
    unittest.main()
