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

    def __init__(
            self, interval, target_func, log_file_path=None, debug=False,
            **target_kwargs):
        """Recursive timer

        Keyword arguments:
            interval: interval time as second
            target_func: callable object to run by timer event.
                         this function should have keyword arguments but NOT arguments.
            log_file_path: file path of log file to output
            debug: enable debug mode if True
            kwargs: object to be passed to the specified target_func

        Returns:
            timer object
        """
        Logger.__init__(self, log_file_path, debug)

        self.interval = interval
        self.target_func = target_func
        self.target_kwargs = target_kwargs

        self.event_stop_timer = threading.Event()
        self.thread_timer = threading.Thread(
            target=self._tick,
            args=(), kwargs={})

    def _tick(self, *args, **kwargs):
        """Tick the time with the specified interval and call the target function.

        Keyword arguments:
            None
        Returns:
            None
        """
        event_tick = threading.Event()
        thread_mainloop = threading.Thread(
            target=self._main_loop,
            args=(event_tick,), kwargs={})

        thread_mainloop.start()

        start_time = datetime.datetime.now()

        while not self.event_stop_timer.isSet():
            time.sleep(0.5)
            now_time = datetime.datetime.now()

            if (now_time - start_time).seconds >= self.interval:
                event_tick.set()
                start_time = now_time

        event_tick.set()
        thread_mainloop.join()

    def _main_loop(self, event_tick, *args, **kwargs):
        """Loop with the specified function.

        Keyword arguments:
            event_tick: event to be set at the timing of calling target_func

        Returns:
            None
        """
        while not self.event_stop_timer.isSet():
            event_tick.wait()

            try:
                self.target_func(**self.target_kwargs)
            except Exception as e:
                self.logger.debug(str(e) + ' error!!!')

            event_tick.clear()

    def start(self):
        """Start the timer thread.

        Args:
            None
        Returns:
            None
        Raises:
            timer.AlreadyRunningErorr if timer already started.
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
