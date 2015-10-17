#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
TS-MPPT-60 monitor application's hook library.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import abc
import threading
import logging


class BaseEventHandler(metaclass=abc.ABCMeta):
    """ Event handeler abstract class. """

    _FORMAT_LOG_MSG = "%(asctime)s %(name)s %(levelname)s: %(message)s"
    _FORMAT_LOG_DATE = "%Y/%m/%d %p %l:%M:%S"

    def __init__(self, callback_to_get_rawdata,
                 log_file_path=None, debug=False):
        self._init_logger(log_file_path, debug)

        self._callback_to_get_rawdata = callback_to_get_rawdata

        self._event_trigger_push = threading.Event()
        self._event_kill_thread = threading.Event()
        self._thread_push = threading.Thread(target=self._handler, args=())
        self._thread_push.setDaemon(True)

    def _init_logger(self, log_file_path, debug):
        self.logger = logging.getLogger(type(self).__name__)

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt=self._FORMAT_LOG_MSG, datefmt=self._FORMAT_LOG_DATE)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        if log_file_path:
            handler = logging.FileHandler(log_file_path, mode="a")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)

    def _handler(self, *args, **kwargs):
        while True:
            try:
                self._event_trigger_push.wait()
                self._event_trigger_push.clear()

                if self._event_kill_thread.is_set():
                    break

                self._push_server()
            except Exception as e:
                self.logger.debug(str(e))
            finally:
                pass

    def _get_rawdata(self):
        if self._callback_to_get_rawdata:
            return self._callback_to_get_rawdata()
        else:
            return None

    def start(self):
        """ Start event handler thread. """
        self._thread_push.start()

    def join(self):
        """ Kill event handler thread. """
        self._event_kill_thread.set()
        self.set_trigger()
        self._thread_push.join(timeout=5)

    def set_trigger(self):
        """ Set trigger to run handler. """
        self._event_trigger_push.set()

    @abc.abstractmethod
    def _push_server(self):
        raise NotImplementedError
