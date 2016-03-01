#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""TS-MPPT-60 monitor application's hook library."""

from keen.client import KeenClient
from solar_monitor.hook import BaseEventHandler


class KeenIoHandler(BaseEventHandler):
    """Event handler class for keen-io."""

    def __init__(self, project_id, write_key, log_file_path=None, debug=False):
        """Initialize instance object.

        Args:
        Returns:
        """
        BaseEventHandler.__init__(self, log_file_path, debug)

        self.client = KeenClient(
            project_id=project_id,
            write_key=write_key)

    def exec(self, rawdata):
        """Update keen-io with datastreams.

        Args:
        Returns:
        """
        data_source = rawdata["source"]
        got_date = rawdata["at"]

        self.logger.debug("send data to keenio at {}".format(got_date))

        datalist_keenio = []
        for monitoring_item, got_data in rawdata["data"].items():
            data_for_keenio = got_data
            data_for_keenio["label"] = monitoring_item
            data_for_keenio["source"] = data_source
            data_for_keenio["keen"] = {"timestamp": got_date.isoformat() + "Z"}
            datalist_keenio.append(data_for_keenio)

        self.client.add_events({"offgrid": datalist_keenio})
