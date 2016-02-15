#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
TS-MPPT-60 monitor application's hook library.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import abc
import queue
import threading
import logging


class BaseEventHandler(metaclass=abc.ABCMeta):
    """Event handeler abstract class."""

    _FORMAT_LOG_MSG = "%(asctime)s %(name)s %(levelname)s: %(message)s"
    _FORMAT_LOG_DATE = "%Y/%m/%d %p %l:%M:%S"

    def __init__(self, log_file_path=None, debug=False, q_max=5):
        """Initialize event handelr.

        Args:
        Returns:
        Exceptions:
        """
        self._init_logger(log_file_path, debug)
        self._thread = threading.Thread(target=self._handler, args=())
        self._thread .setDaemon(True)
        self._q = queue.Queue(q_max)

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
                if 'rawdata' in locals():
                    del rawdata
                rawdata = self._q.get()

                if rawdata is None:
                    break

                self.exec(rawdata)
                self._q.task_done()

            except Exception as e:
                self.logger.debug(str(e) + ' error!!!')

            finally:
                pass

    def start(self):
        """ Start event handler thread. """
        self._thread.start()

    def join(self):
        """ Kill event handler thread. """
        self._q.put(None, timeout=5)
        self._thread.join(timeout=5)

    def put_q(self, item):
        """Put data to the internal queue.

        Args:
            item: data putting to the internal queue
            block: block if True and timeout is not None
            timeout: timeout as second
        Returns:
            None
        Raises:
            queue.Full: if timeout is set and queue is full in the time
        """
        self._q.put_nowait(item)

    def join_q(self):
        """Wait for joining the internal queue.

        Args:
            None
        Returns:
            None
        """
        self._q.join()

    @abc.abstractmethod
    def exec(self, rawdata):
        raise NotImplementedError
