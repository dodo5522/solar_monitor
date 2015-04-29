#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
TS-MPPT-60 monitor application.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is application module to monitor charging status from TS-MPPT-60.
"""

import xively
from hook import EventHandler


class XivelyEventHandler(EventHandler):
    def __init__(
            self, log_file_path=None, debug=False,
            api_key=None, feed_key=None):
        EventHandler.__init__(self, log_file_path, debug)
        self._api_key = api_key
        self._feed_key = feed_key

    def run_handler(self, datastreams, **kwargs):
        """ Update xively feed with datastreams.

        Keyword arguments:
            datastreams: list of xively.Datastream object
        """
        api = xively.XivelyAPIClient(self._api_key)
        feed = api.feeds.get(self._feed_key)

        feed.datastreams = datastreams
        feed.update()
