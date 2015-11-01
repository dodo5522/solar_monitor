#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
TS-MPPT-60 monitor application's hook library.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import subprocess
from . import BaseEventHandler


class BatteryHandler(BaseEventHandler):
    """ Event handler class for battery monitoring. """

    EDGE_NONE = 0
    EDGE_RISING = 1
    EDGE_FALLING = 2

    def __init__(self, callback_to_get_rawdata,
                 log_file_path=None, debug=False, cmd=None,
                 target_edge=EDGE_FALLING, target_volt=12.0):
        BaseEventHandler.__init__(
                self, callback_to_get_rawdata, log_file_path, debug)

        self._cmd = cmd
        self._target_volt = target_volt
        self._target_edge = target_edge
        self.__pre_battery_volt = None

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

    def _get_battery_voltage(self, rawdata):
        for data_list in rawdata["data"]:
            for data in data_list:
                if data["label"] == "Battery Voltage":
                    return data["value"]

        return 0.0

    def exec(self):
        """ Hook battery charge and run some command according to it. """

        rawdata = self._get_rawdata()
        current_battery_volt = self._get_battery_voltage(rawdata)

        self.logger.debug(
                "got data for battery monitor at {}".format(rawdata["at"]))

        if self.__pre_battery_volt is None:
            self.__pre_battery_volt = current_battery_volt

        if self._is_battery_edge_condition(
                current_battery_volt,
                self.__pre_battery_volt,
                self._target_volt,
                self._target_edge) is False:
            self.__pre_battery_volt = current_battery_volt
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
        self.logger.info(stdout_data)
