#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from solar_monitor.event.base import IEventTrigger
from solar_monitor.event.base import IEventListener
from unittest.mock import MagicMock


class TestEventTrigger(unittest.TestCase):
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
        et = IEventTrigger()
        self.assertEqual(et.q_.maxsize, 5)

        et = IEventTrigger(q_max=10)
        self.assertEqual(et.q_.maxsize, 10)

    def test_start_put_stop_event_handlers(self):
        """ 複数EventHandlerを登録し、startコールで全event handlerが開始されること、put_qコールで全event handlerにデータ送信されること、stopコールで全event handlerが停止されることをテストする """
        handler1 = MagicMock(spec=IEventListener)
        handler2 = MagicMock(spec=IEventListener)

        class TestTrigger(IEventTrigger):
            def _is_condition(self, data):
                return True

        et = TestTrigger()
        et.append(handler1)
        et.append(handler2)

        et.start()
        et.put_q(1)
        et.stop()
        et.join()

        self.assertEqual(handler1.start.call_count, 1)
        self.assertEqual(handler2.start.call_count, 1)

        self.assertEqual(handler1.put_q.call_count, 1)
        self.assertEqual(handler2.put_q.call_count, 1)

        self.assertEqual(handler1.stop.call_count, 1)
        self.assertEqual(handler1.join.call_count, 1)
        self.assertEqual(handler2.stop.call_count, 1)
        self.assertEqual(handler2.join.call_count, 1)


if __name__ == "__main__":
    unittest.main()
