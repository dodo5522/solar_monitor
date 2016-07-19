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

"""
Base event class definition especially for trigger/handler. The inheritance
tree structure is like below. These event handler class objects work with
threading by the data or configuration set when initialized.

IEvent
   |- IEventTrigger
   |    |- DataIsUpdatedTrigger     : Catch the timing of any data updated.
   |    |- BatteryLowTrigger        : Catch the timing of low battery voltage.
   |    |- BatteryFullTrigger       : Catch the timing of battery charge completion.
   |    |- ...
   |    `- PanelTempHighTrigger     : Catch the timing of solar panel's temparature getting too high.
   |
   `- IEventHandler
        |- SystemHaltEventHandler   : Shutdown some devices consumpting power to save it.
        |- KeenIoEventHandler       : Upload the system status data to KeenIO service.
        |- XivelyEventHandler       : Upload the system status data to Xively service.
        |- ...
        `- TweetEventHandler        : Tweet the system status to Twitter service.

Event trigger class objects can have multiple event handler class objects. For
example, if you want to tweet the battery voltage and shutdown some consumpting
devices when battery voltage getting low, you make a BatteryLowTrigger object to
have TweetEventHandler and SystemHaltEventHandler objects.
"""

from queue import Queue
from threading import Thread


class IEvent(object):
    """ Base class to handle some event ex. trigger/handler.

    Args:
        condition_func: callable object to return boolean if trigger condition
            is true or not. If None or not callable, the condition is treated
            as always False.
        run_in_condition: Procedure to run if the condition is_condition()
            method returns True.
        q_max: max queue number
    Returns:
        Instance object
    """

    def __init__(self, is_condition=None, run_in_condition=None, q_max=5):
        self.thread_ = Thread(
            target=self._thread_main, name=type(self).__name__, args=())
        self.q_ = Queue(q_max)
        self.is_condition_ = is_condition
        self.run_in_condition_ = run_in_condition

    def _thread_main(self):
        """ Event trigger loop thread function. The role is to receive queue
            having raw data sent by main loop to monitor solar system, and pass
            it to event handlers already registered. This thread is joined if
            the received queue is None.

        Raises:
            TypeError: If run_in_condition is None when initialize this object.
        """
        while True:
            if "got_data" in locals():
                del got_data

            got_data = self.q_.get()
            self.q_.task_done()

            if got_data is None:
                break

            if not self.is_condition_:
                continue
            if not hasattr(self.is_condition_, "__call__"):
                continue
            if not self.is_condition_(got_data):
                continue

            self.run_in_condition_(got_data)

    def start(self):
        """ Start the thread of event trigger loop.

        Exception:
            RuntimeError: Raises if starting this thread twice.
        """
        self.thread_.start()

    def stop(self):
        """ Stop the thread of event trigger loop. Need to call join() method
            to terminate this thread completely.
        """
        self.q_.put(None, timeout=5)

    def join(self):
        """ Wait and block until this thread is teminated completely. """
        self.thread_.join(timeout=5)

    def put_q(self, data):
        """ Put data to the internal queue which is passed to exec() method.

        Args:
            data: data putting to the internal queue
        Raises:
            queue.Full: if timeout is set and queue is full in the time
        """
        self.q_.put_nowait(data)

    def join_q(self):
        """ Wait for the internal queue received and done. """
        self.q_.join()


class IEventTrigger(IEvent):
    """ Event trigger class. Must implement _is_condition() and
        _run_in_condition() method.

    Args:
        q_max: max queue number
    Returns:
        Instance object
    """

    def __init__(self, q_max=5):
        IEvent.__init__(self, is_condition=self._is_condition,
                        run_in_condition=self._run_in_condition,
                        q_max=q_max)
        self.event_handlers_ = []

    def __len__(self):
        return len(self.event_handlers_)

    def _is_condition(self, data):
        """ Trigger condition is matched or not. This method should be
            implented in inherited class.

        Args:
            data: To judge the condition.
        Returns:
            True if the trigger condition is matched.
        """
        raise NotImplementedError

    def _run_in_condition(self, data):
        """ Procedure to run if the condition _is_condition() method returns
            True.

        Args:
            data: Pass to the registered event handlers.
        """
        for event_handler in self.event_handlers_:
            event_handler.put_q(data)
        for event_handler in self.event_handlers_:
            event_handler.join_q()

    def append(self, event_handler):
        """ Register a event handler object should be triggerd if the condition
            is matched.

        Args:
            event_handler: Event handler object.
        """
        self.event_handlers_.append(event_handler)


class IEventHandler(IEvent):
    """ Event handler class. Must implement _run() method.
Args:
        q_max: max queue number
    Returns:
        Instance object
    """

    def __init__(self, q_max=5):
        IEvent.__init__(self, run_in_condition=self._run, q_max=q_max)

    def _run(self, data):
        """ Procedure to run when data received from trigger thread.

        Args:
            data: Pass to the registered event handlers.
        """
        raise NotImplementedError
