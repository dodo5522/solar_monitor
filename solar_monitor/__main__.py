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
import tsmppt60_driver as driver
from solar_monitor.hook.battery import BatteryHandler
from solar_monitor.hook.xively import XivelyHandler
from solar_monitor.hook.keenio import KeenIoHandler
from solar_monitor.timer import RecursiveTimer


class Main(object):
    """main routine class definition.
    """
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
            "--get-all-status",
            action='store_false',
            default=True,
            help="Get all status of charge controller"
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

        if self.args.battery_monitor_enabled:
            self._event_handlers.append(
                BatteryHandler(
                    log_file_path=self.args.log_file,
                    debug=self.args.debug,
                    cmd=self.args.battery_limit_hook_script,
                    target_edge=BatteryHandler.EDGE_FALLING,
                    threshold_voltage=self.args.battery_limit))

        if self.args.keenio_project_id and self.args.keenio_write_key:
            self._event_handlers.append(
                KeenIoHandler(
                    project_id=self.args.keenio_project_id,
                    write_key=self.args.keenio_write_key,
                    log_file_path=self.args.log_file,
                    debug=self.args.debug))

        if self.args.xively_api_key and self.args.xively_feed_key:
            self._event_handlers.append(
                XivelyHandler(
                    api_key=self.args.xively_api_key,
                    feed_key=self.args.xively_feed_key,
                    log_file_path=self.args.log_file,
                    debug=self.args.debug))

        for handler in self._event_handlers:
            handler.start()

    def __call__(self):
        if self.args.just_get_status:
            self._timer_handler()
        else:
            timer = RecursiveTimer(self.args.interval, self._timer_handler)

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

    def _timer_handler(self, **kwargs):
        """ Monitor charge controller and update database like xively or
            internal database. This method should be called with a timer.

        Args:
            kwargs: keyword argument object
        Returns:
            None
        Exceptions:
            queue.Full: If queue of event handler is full
        """
        system_status = driver.SystemStatus(self.args.host_name)

        now = datetime.datetime.utcnow()
        got_data = system_status.get(self.args.get_all_status)

        rawdata = {}
        rawdata["source"] = "solar"
        rawdata["data"] = got_data
        rawdata["at"] = now

        for key, data in got_data.items():
            self.logger.info(
                "{date}: {group}, {elem}, {value}[{unit}]".format(
                    date=now, group=data["group"], elem=key,
                    value=str(data["value"]), unit=data["unit"]))

        for handler in self._event_handlers:
            handler.put_q(rawdata)

        for handler in self._event_handlers:
            handler.join_q()


def main():
    """Just call main function."""
    Main()()
