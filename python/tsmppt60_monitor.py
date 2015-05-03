#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
TS-MPPT-60 monitor application.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is application module to monitor charging status from TS-MPPT-60.
"""

import logging
import time
import argparse
import datetime
import xively
from timer import RecursiveTimer
from driver import livedata
from hook import BatteryEventHandler
from hook import XivelyEventHandler

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
            "-a", "--api-key",
            type=str,
            help="Xively API key string"
        )
        arg.add_argument(
            "-f", "--feed-key",
            type=int,
            help="Xively feed key"
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

        if self.args.debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def _init_event_handlers(self):
        # FIXME: want to support some internal database like sqlite.
        self._event_handlers = (
            XivelyEventHandler(
                self.args.log_file, self.args.debug,
                api_key=self.args.api_key,
                feed_key=self.args.feed_key),
            BatteryEventHandler(
                self.args.log_file, self.args.debug,
                cmd="/usr/local/bin/remote_shutdown.sh",
                target_edge=BatteryEventHandler.EDGE_FALLING,
                target_volt=11.5),
        )

    def __call__(self):
        if self.args.just_get_status:
            for data in self.get_current_streams(self.args.host_name):
                self.logger.info("id:{0}, value:{1}".format(
                    data._data["id"], data._data["current_value"]))
        else:
            timer = RecursiveTimer(self.monitor, self.args.interval)

            try:
                timer.start()
                while True:
                    time.sleep(10)
            except KeyboardInterrupt:
                timer.cancel()

    def monitor(self):
        """ Monitor charge controller and update database like xively or
            internal database. This method should be called with a timer.
        """
        datastreams = self.get_current_streams(self.args.host_name)

        for event_handler in self._event_handlers:
            event_handler.run_handler(datastreams)

    def get_current_streams(self, host_name):
        """ Get status data from charge controller and convert them to data
            streams list for xively.

        Keyword arguments:
            host_name: ip address like 192.168.1.20 or
                       host name can be resolved by DNS

        Returns: xively.Datastream list
        """
        now = datetime.datetime.utcnow()
        self.logger.debug(now)

        datastreams = []
        live = livedata.LiveData(host_name)

        for group in live:
            for status_all in live[group].get_all_status():
                self.logger.debug(group + ": " + ", ".join(status_all))

                datastreams.append(
                    xively.Datastream(
                        id="".join(status_all[0].split()),
                        current_value=float(status_all[1]),
                        at=now
                    )
                )

        return datastreams


if __name__ == "__main__":
    main = Main()
    main()
