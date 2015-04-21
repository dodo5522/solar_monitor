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
import subprocess
import xively
from timer import RecursiveTimer
from driver import livedata

__author__ = "Takashi Ando"
__version__ = "0.0.2"
__copyright__ = "Copyright 2015, My own project"
__license__ = "GPL"


class Main(object):
    """ main routine class """
    _FORMAT_LOG_MSG = "%(asctime)s %(name)s %(levelname)s: %(message)s"
    _FORMAT_LOG_DATE = "%Y/%m/%d %p %l:%M:%S"

    EDGE_NONE = 0
    EDGE_RISING = 1
    EDGE_FALLING = 2

    def __init__(self):
        self._init_args()
        self._init_logger()
        self._init_data_handlers()

        self.__pre_battery_volt = None

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

    def _init_data_handlers(self):
        # FIXME: want to support some internal database like sqlite.
        self._event_handlers = (
            (self._update_xively_with,
             {}),
            (self._update_sqlite_with,
             {}),
            (self._hook_battery_charge,
             {"cmd": "/tmp/remote_shutdown.sh",
              "target_edge": self.EDGE_FALLING,
              "target_volt": 12.02})
        )

    def _update_xively_with(self, datastreams, **kwargs):
        """ Update xively feed with data got with get_current_streams().

        Keyword arguments:
            datastreams: list of xively.Datastream object
        """
        api = xively.XivelyAPIClient(self.args.api_key)
        feed = api.feeds.get(self.args.feed_key)

        feed.datastreams = datastreams
        feed.update()

    def _update_sqlite_with(self, datastreams, **kwargs):
        """ Update interanl database with data got with get_current_streams().

        Keyword arguments:
            datastreams: list of xively.Datastream object
        """
        pass

    def _is_battery_edge_condition(
            self, cur_volt, prev_volt, target_volt, target_edge):
        """ Check if the condition of target.

        Keyword arguments:
            cur_volt: current voltage of battery
            target_volt: target (threshold) voltage of battery
            target_edge: falling or rising target_edge

        Returns: True if condition is matched
        """
        if prev_volt is None:
            return False

        if cur_volt < prev_volt:
            cur_edge = self.EDGE_FALLING
        elif cur_volt > prev_volt:
            cur_edge = self.EDGE_RISING
        else:
            cur_edge = self.EDGE_NONE

        self.logger.debug("cur_volt: " + str(cur_volt))
        self.logger.debug("prev_volt: " + str(prev_volt))
        self.logger.debug("cur_edge: " + str(cur_edge))
        self.logger.debug("target_edge: " + str(target_edge))

        condition = False

        if target_edge is self.EDGE_RISING:
            if cur_edge is self.EDGE_RISING:
                if cur_volt > target_volt:
                    condition = True
        elif target_edge is self.EDGE_FALLING:
            if cur_edge is self.EDGE_FALLING:
                if cur_volt < target_volt:
                    condition = True

        return condition

    def _hook_battery_charge(self, datastreams,
                             cmd=None, target_volt=0, target_edge=EDGE_NONE):
        """ Hook battery charge and run some command according to it.

        Keyword arguments:
            datastreams: list of xively.Datastream object
            cmd: command to run if condition is True
            target_volt: target (threshold) voltage of battery
            target_edge: falling or rising target_edge
        """
        for datastream in datastreams:
            if datastream._data["id"] == "BatteryVoltage":
                current_battery_volt = float(datastream._data["current_value"])

                if self.__pre_battery_volt is None:
                    self.__pre_battery_volt = current_battery_volt

                break
        else:
            return

        if self._is_battery_edge_condition(
                current_battery_volt,
                self.__pre_battery_volt,
                target_volt, target_edge) is False:
            self.__pre_battery_volt = current_battery_volt
            return

        proc = subprocess.Popen(
            cmd.split(),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_data, stderr_data = proc.communicate()

        self.logger.info(
            "{} is executed and returned below values.".format(cmd))
        self.logger.info(stdout_data)

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

        for event_handler, kwargs in self._event_handlers:
            event_handler(datastreams, **kwargs)

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
