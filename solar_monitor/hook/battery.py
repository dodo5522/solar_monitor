#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""TS-MPPT-60 monitor application's hook library."""

import subprocess
from solar_monitor.hook import BaseBatteryEventHandler


class BatteryHandler(BaseBatteryEventHandler):
    """Event handler class for battery monitoring."""

    def __init__(self, **kwargs):
        """Initialize instance of BatteryHandler class. The arguments are same as the parent class BaseBatteryEventHandler.

        Args:
            log_file_path: path to output log data
            debug: debug log is output if True
            q_max: max queue number
            cmd: command to execute when the specified event is triggered
            target_edge: folling or rising edge if specified
            threshold_voltage: the threshold of voltage to judge the event is triggered
        Returns:
            Instance object
        """
        BaseBatteryEventHandler.__init__(self, **kwargs)

        self._pre_battery_volt = None

    def exec(self, rawdata):
        """Hook battery charge and run some command according to it.

        Args:
            rawdata: dict of rawdata.
        Returns:
            None
        """
        if "Battery Voltage" in rawdata["data"]:
            current_battery_volt = rawdata["data"]["Battery Voltage"]["value"]
        else:
            current_battery_volt = 0.0

        self.logger.debug(
            "got data for battery monitor at {}".format(rawdata["at"]))

        if self._pre_battery_volt is None:
            self._pre_battery_volt = current_battery_volt

        if self.is_battery_event_triggered(
                current_battery_volt,
                self._pre_battery_volt) is False:
            self._pre_battery_volt = current_battery_volt
            return

        if self._cmd is None:
            return

        self.logger.debug("running command {}".format(self._cmd))

        proc = subprocess.Popen(
            self._cmd.split(),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_data, stderr_data = proc.communicate()

        self.logger.info(
            "{} is executed and returned below values.".format(self._cmd))
        self.logger.info(stdout_data.decode())
