#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
TS-MPPT-60 monitor application's hook library.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import xively
from . import BaseEventHandler


class XivelyHandler(BaseEventHandler):
    """ Event handler class for xively. """

    def __init__(self, callback_to_get_rawdata, api_key, feed_key,
                 log_file_path=None, debug=False):
        BaseEventHandler.__init__(
                self, callback_to_get_rawdata, log_file_path, debug)

        self._api_key = api_key
        self._feed_key = feed_key

    def exec(self):
        """ Update xively feed with datastreams. """

        api = xively.XivelyAPIClient(self._api_key)
        feed = api.feeds.get(self._feed_key)

        rawdata = self._get_rawdata()

        self.logger.debug("send data to xively at {}".format(rawdata["at"]))

        datastreams = []
        for key, data in rawdata["data"].items():
            datastreams.append(
                xively.Datastream(
                    id="".join(key.split()),
                    current_value=data["value"],
                    at=rawdata["at"]
                )
            )

        feed.datastreams = datastreams
        feed.update()
