#!/usr/bin/env python3
# -*- coding:utf-8 -*-

#   Copyright 2016 Takashi Ando - http://blog.rinka-blossom.com/
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""TS-MPPT-60 timer library module."""

import threading
import time

from solar_monitor import logger
from datetime import datetime


class NotStartedYetError(Exception):
    """Exception if timer is canceled even though it's not started yet."""
    pass


class AlreadyRunningError(Exception):
    """Exception if timer is already running."""
    pass


class RecursiveTimer(object):
    """Class of timer for recursively running function.

    Keyword arguments:
        interval: interval time as second
        target_func: callable object to run by timer event.
                     this function should have keyword arguments but NOT arguments.
        debug: enable debug mode if True
        kwargs: object to be passed to the specified target_func

    Returns:
        timer object
    """

    def __init__(self, interval, target_func, **target_kwargs):
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
        start_time = datetime.now()

        while True:
            time.sleep(0.5)

            if self.event_stop_timer.isSet():
                break

            if 'now_time' in locals():
                del now_time
            now_time = datetime.now()

            if (now_time - start_time).seconds >= self.interval:
                if 'start_time' in locals():
                    del start_time
                start_time = now_time
                event_tick.set()

        event_tick.set()
        thread_mainloop.join()

    def _main_loop(self, event_tick, *args, **kwargs):
        """Loop with the specified function.

        Keyword arguments:
            event_tick: event to be set at the timing of calling target_func

        Returns:
            None
        """
        while True:
            event_tick.wait()
            event_tick.clear()

            if self.event_stop_timer.isSet():
                break

            try:
                self.target_func(**self.target_kwargs)
            except Exception as e:
                logger.debug(str(e) + ' error!!!')

    def start(self):
        """Start the timer thread.

        Args:
            None
        Returns:
            None
        Raises:
            timer.AlreadyRunningError if timer already started.
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
        Raises:
            timer.NotStartedYetError if timer is canceled even though it's not started yet.
        """
        if self.thread_timer.isAlive():
            self.event_stop_timer.set()
            self.thread_timer.join()
        else:
            raise NotStartedYetError("timer is not running")

    def is_alive(self):
        """Test if the timer thread is alive.

        Args:
            None
        Returns:
            True if alive
        >>> rt.start()
        >>> rt.is_alive()
        True
        >>> rt.cancel()
        >>> rt.is_alive()
        False
        """
        return self.thread_timer.isAlive()

if __name__ == '__main__':
    import doctest
    doctest.testmod(extraglobs={'rt': RecursiveTimer(3, lambda: print(datetime.now()))})
