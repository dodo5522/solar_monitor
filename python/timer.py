#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
TS-MPPT-60 timer library module.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import time
import datetime
import threading
from . import Logger


class RecursiveTimer(Logger):
    """ Class of timer for recursively running function. """
    def __init__(self, target, interval=300, **kwargs):
        """ Recursive timer

        Arguments:
            target: callable object to run by timer event.
            interval: interval time as second
        """
        Logger.__init__(
            self,
            log_file_path=getattr(kwargs, "log_file_path"),
            debug=getattr(kwargs, "debug"))

        self._event_kill = threading.Event()
        self._thread_tick = threading.Thread(
            target=self._tick,
            args=(target, interval))

    def _tick(self, *args, **kwargs):
        target = args[0]
        interval = args[1]

        event_tick = threading.Event()
        thread_target = threading.Thread(
            target=self._recurs_func,
            args=(target, event_tick))

        thread_target.start()

        start_time = datetime.datetime.now()

        while not self._event_kill.isSet():
            time.sleep(1)
            now_time = datetime.datetime.now()

            if (now_time - start_time).seconds >= interval:
                event_tick.set()
                start_time = now_time

        event_tick.set()
        thread_target.join()

    def _recurs_func(self, *args, **kwargs):
        target = args[0]
        event_tick = args[1]

        while not self._event_kill.isSet():
            event_tick.wait()

            try:
                target()
            except Exception as err:
                self.logger.debug(str(err))

            event_tick.clear()

    def start(self):
        if not self._thread_tick.isAlive():
            self._event_kill.clear()
            self._thread_tick.start()
        else:
            raise SystemError("timer thread is already run")

    def cancel(self):
        self._event_kill.set()
        self._thread_tick.join()
