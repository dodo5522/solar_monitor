#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
TS-MPPT-60 monitor application's hook library.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from m2x.client import M2XClient
from m2x.utils import to_iso
from . import BaseEventHandler


class EventHandler(BaseEventHandler):
    def __init__(
            self, api_key, device_key, log_file_path=None, debug=False):
        BaseEventHandler.__init__(self, log_file_path, debug)
        self._api_key = api_key
        self._device_key = device_key

        client = M2XClient(key=api_key)
        self.device = client.api.device(id=device_key)

    def run_handler(self, rawdata, **kwargs):
        names = [stream.data.get("name") for stream in self.device.streams()]

        values = {}
        for data_list in rawdata["data"]:
            for data in data_list:
                ds_name = "".join(data["label"].split())

                try:
                    names.index(ds_name)
                except ValueError:
                    self.logger.debug(ds_name + " is not found in m2x.")
                    continue

                ds_value = str(data["value"])
                ds_at = rawdata["at"]

                values[ds_name] = []
                values[ds_name].append(
                    {"value": str(ds_value),
                     "timestamp": to_iso(ds_at.utcnow())})

                self.logger.debug(ds_name)
                self.logger.debug(ds_at)
                self.logger.debug(ds_value)

        all_data = {"values": values, "location": None}
        res = self.device.post_updates(**all_data)
        self.logger.info(
            "device update returns status {}".format(res["status"]))
