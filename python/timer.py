#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
TS-MPPT-60 timer library module.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import time
import datetime
import threading


class RecursiveTimer(object):
    """ Class of timer for recursively running function. """
    def __init__(self, func, interval_sec=300, is_resursive=True):
        """ Recursive timer if is_recursive is True.

        Arguments:
            func: callable object to run by timer event.
            interval_sec: interval time as second
            is_recursive: func is called recursively if true
        """
        self._func = func
        self._thread_tick = threading.Thread(
            target=self._tick, args=(interval_sec, is_resursive))

        self._event_tick = threading.Event()
        self._event_kill = threading.Event()

    def _tick(self, *args, **kwargs):
        interval_sec = args[0]
        is_recursive = args[1]

        if is_recursive:
            thread_main = threading.Thread(target=self._main)
            thread_main.start()

            start_time = datetime.datetime.now

            while not self._event_kill.isSet():
                time.sleep(1)
                now_time = datetime.datetime.now

                if (now_time - start_time).seconds > interval_sec:
                    self._event_tick.set()
                    start_time = now_time

            thread_main.join()
        else:
            time.sleep(interval_sec)
            self._func()

    def _main(self):
        while not self._event_kill.isSet():
            self._event_tick.wait()
            self._func()
            self._event_tick.clear()

    def start(self):
        if not self._thread_tick.isAlive():
            self._event_kill.clear()
            self._event_tick.clear()
            self._thread_tick.start()
        else:
            raise SystemError("timer thread is already run")

    def cancel(self):
        self._event_kill.set()
        self._thread_tick.join()
