#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
TS-MPPT-60 monitor application's hook library.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from keen.client import KeenClient
from . import BaseEventHandler


class EventHandler(BaseEventHandler):
    def __init__(
            self, project_id, write_key, log_file_path=None, debug=False):
        BaseEventHandler.__init__(self, log_file_path, debug)
        self._project_id = project_id
        self._write_key = write_key

    def run_handler(self, rawdata, **kwargs):
        """ Update keen-io with datastreams.

        Keyword arguments:
            rawdata: dict with got time and data streams
        """
        client = KeenClient(
            project_id=self._project_id,
            write_key=self._write_key)

        for data_list in rawdata["data"]:
            for data in data_list:
                _newdata = data.copy()
                _newdata["source"] = rawdata["source"]
                client.add_event("offgrid", _newdata, timestamp=rawdata["at"])
