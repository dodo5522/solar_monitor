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
        self._event_handlers = (
            hook.xively.EventHandler(
                self.args.xively_api_key, self.args.xively_feed_key,
                self.args.log_file, self.args.debug),
            hook.m2x.EventHandler(
                self.args.m2x_api_key, self.args.m2x_device_key,
                self.args.log_file, self.args.debug),
            hook.battery.EventHandler(
                self.args.log_file, self.args.debug,
                cmd="/usr/local/bin/remote_shutdown.sh",
                target_edge=hook.battery.EventHandler.EDGE_FALLING,
                target_volt=11.5),
            hook.keenio.EventHandler(
                self.args.keenio_project_id, self.args.keenio_write_key,
                self.args.log_file, self.args.debug),
        )

    def __call__(self):
        if self.args.just_get_status:
            self.get_current_streams(self.args.host_name)
        else:
            self._init_event_handlers()
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
        stream = self.get_current_streams(self.args.host_name)

        for event_handler in self._event_handlers:
            event_handler.run_handler(stream)

    def get_current_streams(self, host_name):
        """ Get status data from charge controller and convert them to data
            streams list.

        Keyword arguments:
            host_name: ip address like 192.168.1.20 or
                       host name can be resolved by DNS

        Returns:
            datetime and datastreams list got from get_all_status()
        """
        now = datetime.datetime.utcnow()
        groups = livedata.LiveStatus(host_name)
        ret_dict = {
            "source": "solar",
            "data": [group.get_all_status() for group in groups],
            "at": now}

        for data_list in ret_dict["data"]:
            for data in data_list:
                self.logger.info(
                    "{}: {}, {}, {}, {} from {}".format(
                        ret_dict["at"], data["group"], data["label"],
                        str(data["value"]), data["unit"], ret_dict["source"]))

        return ret_dict


if __name__ == "__main__":
    main = Main()
    main()
