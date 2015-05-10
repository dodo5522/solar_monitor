#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
TS-MPPT-60 monitor application's hook library.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from m2x.client import M2XClient
from m2x.utils import to_iso
from . import EventHandler


class M2XEventHandler(EventHandler):
    def __init__(
            self, log_file_path=None, debug=False,
            api_key=None, device_key=None):
        EventHandler.__init__(self, log_file_path, debug)
        self._api_key = api_key
        self._device_key = device_key

        client = m2x.client.M2XClient(key=api_key)
        self.device = client.api.device(id=device_key)

    def run_handler(self, datastreams, **kwargs):
        names = []
        for stream in self.device.streams():
            names.append(stream.data.get("name"))

        for name in names:
            self.logger.debug(name)

        values = {}
        for ds in datastreams:
            ds_name = ds._data["id"]
            ds_value = ds._data["current_value"]
            ds_at = ds._data["at"]

            try:
                names.index(ds_name)
            except ValueError:
                continue

            values[ds_name] = []
            values[ds_name].append(
                {"value": ds_value, "timestamp": to_iso(ds_at.utcnow())})

            self.logger.debug(ds_name)
            self.logger.debug(ds_at)
            self.logger.debug(ds_value)

        all_data = {"values": values, "location": None}
        print(all_data)

        res = self.device.update(all_data)
        self.logger.debug(
            "device update returns status {}".format(res["status"]))
