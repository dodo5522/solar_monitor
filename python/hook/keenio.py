#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
TS-MPPT-60 monitor application's hook library.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from keen.client import KeenClient
from . import BaseEventHandler


class EventHandler(BaseEventHandler):
    """ Event handler class for keen-io. """

    def __init__(self, callback_to_get_rawdata, project_id, write_key,
                 log_file_path=None, debug=False):
        BaseEventHandler.__init__(
                self, callback_to_get_rawdata, log_file_path, debug)

        self._project_id = project_id
        self._write_key = write_key

    def _push_server(self):
        """ Update keen-io with datastreams. """

        client = KeenClient(
            project_id=self._project_id,
            write_key=self._write_key)

        rawdata = self._get_rawdata()

        for data_list in rawdata["data"]:
            for data in data_list:
                _newdata = data.copy()
                _newdata["source"] = rawdata["source"]
                client.add_event("offgrid", _newdata, timestamp=rawdata["at"])
