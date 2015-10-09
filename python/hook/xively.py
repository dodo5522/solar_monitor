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
            self, log_file_path=None, debug=False,
            api_key=None, feed_key=None):
        BaseEventHandler.__init__(self, log_file_path, debug)
        self._api_key = api_key
        self._feed_key = feed_key

    def run_handler(self, rawdatas, **kwargs):
        """ Update xively feed with datastreams.

        Keyword arguments:
            rawdatas: tuple of raw data
        """
        api = xively.XivelyAPIClient(self._api_key)
        feed = api.feeds.get(self._feed_key)

        datastreams = []
        for rawdata in rawdatas:
            datastreams.append(
                xively.Datastream(
                    id="".join(rawdata["id"].split()),
                    current_value=float(rawdata["data"]["value"]),
                    at=rawdata["at"]
                )
            )

        feed.datastreams = datastreams
        feed.update()
