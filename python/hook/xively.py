#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
TS-MPPT-60 monitor application's hook library.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import xively
from . import BaseEventHandler


class EventHandler(BaseEventHandler):
    def __init__(
            self, api_key, feed_key, log_file_path=None, debug=False):
        BaseEventHandler.__init__(self, log_file_path, debug)
        self._api_key = api_key
        self._feed_key = feed_key

    def run_handler(self, rawdata, **kwargs):
        """ Update xively feed with datastreams.

        Keyword arguments:
            rawdata: dict of raw data
        """
        api = xively.XivelyAPIClient(self._api_key)
        feed = api.feeds.get(self._feed_key)

        datastreams = []
        for data_list in rawdata["data"]:
            for data in data_list:
                datastreams.append(
                    xively.Datastream(
                        id="".join(data["label"].split()),
                        current_value=data["value"],
                        at=rawdata["at"]
                    )
                )

        feed.datastreams = datastreams
        feed.update()
