#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""TS-MPPT-60 monitor event hook library."""

import xively
from solar_monitor.hook import BaseEventHandler


class XivelyHandler(BaseEventHandler):
    """ Event handler class for xively. """

    def __init__(self, api_key, feed_key, log_file_path=None, debug=False):
        """Initialize instance object.

        Args:
        Returns:
        """
        BaseEventHandler.__init__(self, log_file_path, debug)

        api = xively.XivelyAPIClient(api_key)
        self.feed = api.feeds.get(feed_key)

    def exec(self, rawdata):
        """Update xively feed with datastreams.

        Args:
        Returns:
        """
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

        self.feed.datastreams = datastreams
        self.feed.update()
