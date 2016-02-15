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
        self.logger.debug("send data to keenio at {}".format(rawdata["at"]))

        _newdata_list = []
        for key, data in rawdata["data"].items():
            _newdata = data
            _newdata["label"] = key
            _newdata["source"] = rawdata["source"]
            _newdata["keen"] = {"timestamp": rawdata["at"].isoformat() + "Z"}
            _newdata_list.append(_newdata)

        self.client.add_events({"offgrid": _newdata_list})
