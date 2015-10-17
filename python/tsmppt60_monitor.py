#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
TS-MPPT-60 monitor application.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is application module to monitor charging status from TS-MPPT-60.
"""

import threading
import logging
import time
import argparse
import datetime
import hook.battery
import hook.xively
import hook.m2x
import hook.keenio
from timer import RecursiveTimer
from driver import livedata

__author__ = "Takashi Ando"
__version__ = "1.1.1"
__copyright__ = "Copyright 2015, My own project"
__license__ = "GPL"


class Main(object):
    """ main routine class """
    _FORMAT_LOG_MSG = "%(asctime)s %(name)s %(levelname)s: %(message)s"
    _FORMAT_LOG_DATE = "%Y/%m/%d %p %l:%M:%S"

    def __init__(self):
        self._init_args()
        self._init_logger()
        self._init_event_handlers()

        self._lock_rawdata = threading.Lock()
        self._rawdata = {"source": "solar", "data": None, "at": None}

    def _init_args(self):
        arg = argparse.ArgumentParser(
            description="main program to test TS-MPPT-60 monitor modules")
        arg.add_argument(
            "-n", "--host-name",
            type=str,
            default="192.168.1.20",
            help="TS-MPPT-60 host address"
        )
        arg.add_argument(
            "-xa", "--xively-api-key",
            type=str,
            nargs='?', default=None, const=None,
            help="Xively API key string"
        )
        arg.add_argument(
            "-xf", "--xively-feed-key",
            type=int,
            nargs='?', default=None, const=None,
            help="Xively feed key"
        )
        arg.add_argument(
            "-ma", "--m2x-api-key",
            type=str,
            nargs='?', default=None, const=None,
            help="M2X API key string"
        )
        arg.add_argument(
            "-md", "--m2x-device-key",
            type=str,
            nargs='?', default=None, const=None,
            help="M2X feed key"
        )
        arg.add_argument(
            "-kp", "--keenio-project-id",
            type=str,
            nargs='?', default=None, const=None,
            help="keenio project id string"
        )
        arg.add_argument(
            "-kw", "--keenio-write-key",
            type=str,
            nargs='?', default=None, const=None,
            help="keenio write key"
        )
        arg.add_argument(
            "-be", "--battery-monitor-enabled",
            action="store_true",
            default=False,
            help="enable battery monitor"
        )
        arg.add_argument(
            "-bl", "--battery-limit",
            type=float,
            nargs='?', default=11.5, const=11.5,
            help="battery voltage limit like 11.5"
        )
        arg.add_argument(
            "-bs", "--battery-limit-hook-script",
            type=str, nargs='?',
            default="/usr/local/bin/remote_shutdown.sh",
            const="/usr/local/bin/remote_shutdown.sh",
            help="path to hook sript run at limit of battery"
        )
        arg.add_argument(
            "-i", "--interval",
            type=int,
            default=300,
            help="Xively update interval with sec"
        )
        arg.add_argument(
            "-l", "--log-file",
            type=str,
            default=None,
            help="log file path to output"
        )
        arg.add_argument(
            "--just-get-status",
            action='store_true',
            default=False,
            help="Just get status of charge controller"
        )
        arg.add_argument(
            "--debug",
            action='store_true',
            default=False,
            help="Enable debug mode"
        )

        self.args = arg.parse_args()

    def _init_logger(self):
        self.logger = logging.getLogger("main")

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt=self._FORMAT_LOG_MSG, datefmt=self._FORMAT_LOG_DATE)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        if self.args.log_file:
            handler = logging.FileHandler(self.args.log_file, mode="a")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.logger.setLevel(
                logging.DEBUG if self.args.debug else logging.INFO)

    def _init_event_handlers(self):
        # FIXME: want to support some internal database like sqlite.
        self._event_handlers = []

        if self.args.xively_api_key and self.args.xively_feed_key:
            self._event_handlers.append(
                hook.xively.EventHandler(
                    self.get_rawdata,
                    self.args.xively_api_key, self.args.xively_feed_key,
                    self.args.log_file, self.args.debug))

        if self.args.keenio_project_id and self.args.keenio_write_key:
            self._event_handlers.append(
                hook.keenio.EventHandler(
                    self.get_rawdata,
                    self.args.keenio_project_id, self.args.keenio_write_key,
                    self.args.log_file, self.args.debug))

        if self.args.battery_monitor_enabled:
            self._event_handlers.append(
                hook.battery.EventHandler(
                    self.get_rawdata,
                    self.args.log_file, self.args.debug,
                    cmd=self.args.battery_limit_hook_script,
                    target_edge=hook.battery.EventHandler.EDGE_FALLING,
                    target_volt=self.args.battery_limit))

        for handler in self._event_handlers:
            handler.start()

    def __call__(self):
        if self.args.just_get_status:
            self._timer_handler()
        else:
            timer = RecursiveTimer(self._timer_handler, self.args.interval)

            try:
                timer.start()
                while True:
                    time.sleep(10)
            except Exception as e:
                self.logger.debug(str(e))
            finally:
                timer.cancel()
                for handler in self._event_handlers:
                    handler.join()

    def set_rawdata(self, data, at):
        """ Set rawdata into internal buffer with locked. """
        with self._lock_rawdata:
            self._rawdata["data"] = data
            self._rawdata["at"] = at

    def get_rawdata(self):
        """ Get rawdata with locked. """
        with self._lock_rawdata:
            ret = self._rawdata.copy()

        return ret

    def _timer_handler(self):
        """ Monitor charge controller and update database like xively or
            internal database. This method should be called with a timer.
        """
        groups = livedata.LiveStatus(self.args.host_name)

        self.set_rawdata(
            [group.get_all_status() for group in groups],
            datetime.datetime.utcnow())

        rawdata = self.get_rawdata()
        for data_list in rawdata["data"]:
            for data in data_list:
                self.logger.info(
                    "{}: {}, {}, {}, {} from {}".format(
                        rawdata["at"], data["group"], data["label"],
                        str(data["value"]), data["unit"], rawdata["source"]))

        for handler in self._event_handlers:
            handler.set_trigger()


if __name__ == "__main__":
    main = Main()
    main()
