#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from solar_monitor.event.base import IEventHandler


class TestIEventHandler(unittest.TestCase):
    """ 親クラスのIEventListenerで実施済みテスト以外をテストする """

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

    def test_q_max(self):
        """ queue最大値設定が反映されるかテストする """
        eh = IEventHandler()
        self.assertEqual(eh.q_.maxsize, 5)

        eh = IEventHandler(q_max=10)
        self.assertEqual(eh.q_.maxsize, 10)


if __name__ == "__main__":
    unittest.main()
