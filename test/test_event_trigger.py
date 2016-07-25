#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from threading import Event
from solar_monitor.event.base import IEventListener
from solar_monitor.event.base import IEventTrigger
from solar_monitor.event.base import IEventHandler


class TestEventListener(unittest.TestCase):
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

        el = IEventListener()
        self.assertEqual(5, el.q_.maxsize)

        el = IEventListener(q_max=10)
        self.assertEqual(10, el.q_.maxsize)

    def test_start_stop_and_join(self):
        """ main thread開始と停止をテストする """

        el = IEventListener(is_condition=None, run_in_condition=None)

        el.start()
        self.assertTrue(el.thread_.is_alive())

        el.stop()
        el.join()
        self.assertFalse(el.thread_.is_alive())

    def test_join_error(self):
        """ main thread停止後のjoinでエラーをraiseするパターンをテストする """

        el = IEventListener(is_condition=None, run_in_condition=None)
        el.start()

        self.assertRaises(SystemError, el.join, 0.1)
        self.assertTrue(el.thread_.is_alive())

        # 後のテストを継続するための後始末
        el.stop()
        el.join()

    def test_put_q(self):
        """ queueにputする動作をテストする """
        el = IEventListener()
        el.start()

        el.put_q(1)
        self.assertEqual(el.q_.unfinished_tasks, 1)

        el.join_q()
        self.assertEqual(el.q_.unfinished_tasks, 0)

        el.stop()
        el.join()

    def test_put_q_none(self):
        """ 外部IFを使用してqueueにNoneをputするのは禁止 """
        el = IEventListener()
        el.start()

        self.assertRaises(ValueError, el.put_q, None)

        el.stop()
        el.join()

    def test_is_condition_none(self):
        """ is_condition()がNoneの場合にrun_in_conditionをコールしない """
        e = Event()

        el = IEventListener(is_condition=None, run_in_condition=lambda x: e.set())
        el.start()
        el.put_q(1)
        el.join_q()

        self.assertFalse(e.wait(0.1))

        el.stop()
        el.join()

    def test_is_condition_not_callable(self):
        """ is_condition()がcallableでない場合にrun_in_conditionをコールしない """
        e = Event()
        not_callable_obj = []

        el = IEventListener(is_condition=not_callable_obj, run_in_condition=lambda x: e.set())
        el.start()
        el.put_q(1)
        el.join_q()

        self.assertFalse(e.wait(0.1))

        el.stop()
        el.join()

    def test_is_condition_false(self):
        """ is_condition()がFalseを返す場合にrun_in_conditionをコールしない """
        e = Event()

        el = IEventListener(is_condition=lambda x: False, run_in_condition=lambda x: e.set())
        el.start()
        el.put_q(1)
        el.join_q()

        self.assertFalse(e.wait(0.1))

        el.stop()
        el.join()

    def test_run_in_condition_none(self):
        """ run_in_condition()がNoneの場合に何もしない（例外もraiseしない） """
        el = IEventListener(is_condition=lambda x: True, run_in_condition=None)

        el.start()
        el.put_q(1)
        el.join_q()
        el.stop()
        el.join()

    def test_run_in_condition_callable(self):
        """ run_in_condition()がcallableでない場合に何もしない（例外もraiseしない） """
        not_callable_obj = []
        el = IEventListener(is_condition=lambda x: True, run_in_condition=lambda x: not_callable_obj)

        el.start()
        el.put_q(1)
        el.join_q()
        el.stop()
        el.join()

    def test_run_in_condition(self):
        """ is_condition()がTrueを返す場合にrun_in_conditionをコールする """
        e = Event()

        el = IEventListener(is_condition=lambda x: True, run_in_condition=lambda x: e.set())
        el.start()
        el.put_q(1)
        el.join_q()

        self.assertTrue(e.wait(0.1))

        el.stop()
        el.join()


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

    @unittest.skip
    def test_append(self):
        """ 複数EventHandlerを登録する動作をテストする """
        pass

    @unittest.skip
    def test_start(self):
        """ 複数EventHandlerを開始しつつ、自身も開始することをテストする """
        pass

    @unittest.skip
    def test_stop(self):
        """ 複数EventHandlerを停止しつつ、自身も停止することをテストする """
        pass

    @unittest.skip
    def test_join(self):
        """ 複数EventHandlerをjoinしつつ、自身もjoinすることをテストする """
        pass


class TestEventHandler(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
