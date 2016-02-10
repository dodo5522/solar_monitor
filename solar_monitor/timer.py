#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
TS-MPPT-60 timer library module.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import time
import datetime
import threading
from tsmppt60_driver.base import Logger


class AlreadyRunningError(Exception):
    pass


class RecursiveTimer(Logger):
    """Class of timer for recursively running function.
    """

    def __init__(self, target_func, target_func_arg=None, interval=300, log_file_path=None, debug=False):
        """Recursive timer

        Keyword arguments:
            target_func: callable object to run by timer event.
            target_func_arg: object to be passed to the specified target_func
            interval: interval time as second
            log_file_path: file path of log file to output
            debug: enable debug mode if True

        Returns:
            timer object
        """
        Logger.__init__(self, log_file_path, debug)

        self.event_stop_timer = threading.Event()
        self.thread_timer = threading.Thread(
            target=self._tick,
            args=(target_func, target_func_arg, interval),
            kwargs={})

    def _tick(self, target_func, target_func_arg, interval, **kwargs):
        """Tick the time with the specified interval and call the target function.

        Keyword arguments:
            target_func: target function to be called recursively
            target_func_arg: object to be passed to the specified target_func
            interval: interval time second

        Returns:
            None
        """
        event_tick = threading.Event()
        thread_mainloop = threading.Thread(
            target=self._main_loop,
            args=(target_func, target_func_arg, event_tick))

        thread_mainloop.start()

        start_time = datetime.datetime.now()

        while not self.event_stop_timer.isSet():
            time.sleep(1)
            now_time = datetime.datetime.now()

            if (now_time - start_time).seconds >= interval:
                event_tick.set()
                start_time = now_time

        event_tick.set()
        thread_mainloop.join()

    def _main_loop(self, target_func, target_func_arg, event_tick, **kwargs):
        """Loop with the specified function.

        Keyword arguments:
            target_func: target function to be called recursively
            target_func_arg: object to be passed to the specified target_func
            event_tick: event to be set at the timing of calling target_func

        Returns:
            None
        """
        while not self.event_stop_timer.isSet():
            event_tick.wait()

            try:
                target_func(target_func_arg)
            except Exception as e:
                self.logger.debug(str(e) + ' error!!!')

            event_tick.clear()

    def start(self):
        """Start the timer thread.

        Args:
            None
        Returns:
            None
        """
        if not self.thread_timer.isAlive():
            self.event_stop_timer.clear()
            self.thread_timer.start()
        else:
            raise AlreadyRunningError("timer thread is already run")

    def cancel(self):
        """Stop the timer thread if alive.

        Args:
            None
        Returns:
            None
        """
        if self.thread_timer.isAlive():
            self.event_stop_timer.set()
            self.thread_timer.join()

    def is_alive(self):
        """Test if the timer thread is alive.

        Args:
            None
        Returns:
            True if alive
        """
        return self.thread_timer.isAlive()
