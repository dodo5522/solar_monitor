#!/usr/bin/env python3
# -*- coding:utf-8 -*-

#   Copyright 2016 Takashi Ando - http://blog.rinka-blossom.com/
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import subprocess
import xively
import tweepy
from keen.client import KeenClient
from solar_monitor import logger
from solar_monitor.event.base import IEventHandler


class SystemHaltEventHandler(IEventHandler):
    """  """

    def __init__(self, cmd, q_max=5):
        IEventHandler.__init__(self, q_max=q_max)
        self.cmd_ = cmd

    def _run(self, data):
        """ Procedure to run when data received from trigger thread.

        Args:
            data: Pass to the registered event handlers.
        """
        if not self.cmd_:
            logger.warning("Running command is not set.")
            return

        proc = subprocess.Popen(
            self.cmd_.split(),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_data, stderr_data = proc.communicate()

        logger.info("{} is executed and returned blow data.".format(self.cmd_))
        logger.info(stdout_data.decode())


class KeenIoEventHandler(IEventHandler):
    """  """

    def __init__(self, project_id, write_key, q_max=5):
        IEventHandler.__init__(self, q_max=q_max)

        self.client_ = KeenClient(
            project_id=project_id,
            write_key=write_key)

    def _run(self, data):
        """ Procedure to run when data received from trigger thread.

        Args:
            data: Pass to the registered event handlers.
        """
        data_source = data["source"]
        at = data["at"]

        upload_items = []
        for label, datum in data["data"].items():
            upload_item = datum
            upload_item["label"] = label
            upload_item["source"] = data_source
            upload_item["keen"] = {"timestamp": "{}Z".format(at.isoformat())}
            upload_items.append(upload_item)

        self.client_.add_events({"offgrid": upload_items})

        logger.info("{} sent data to keenio at {}".format(
            type(self).__name__, at))


class XivelyEventHandler(IEventHandler):
    """  """

    def __init__(self, api_key, feed_key, q_max=5):
        IEventHandler.__init__(self, q_max=q_max)

        api = xively.XivelyAPIClient(api_key)
        self.client_ = api.feeds.get(feed_key)

    def _run(self, data):
        """ Procedure to run when data received from trigger thread.

        Args:
            data: Pass to the registered event handlers.
        """
        at = data["at"]

        datastreams = []
        for key, data in data["data"].items():
            datastreams.append(
                xively.Datastream(
                    id="".join(key.split()),
                    current_value=data["value"],
                    at=at
                )
            )

        self.client_.datastreams = datastreams
        self.client_.update()

        logger.info("{} sent data to xively at {}".format(
            type(self).__name__, at))


class TweetBotEventHandler(IEventHandler):
    def __init__(self, path_conf, q_max=5):
        IEventHandler.__init__(self, q_max=q_max)

        self.get_keys(path_conf)

        auth = tweepy.OAuthHandler(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret)

        auth.set_access_token(key=self.key, secret=self.secret)

        self.api_ = tweepy.API(auth)

    def get_keys(self, path_conf):
        with open(path_conf) as f:
            keys = {line.split("=")[0]: line.split("=")[1] for line in f.readlines()}

        logger.debug(str(keys))

        self.consumer_key = keys["twitter_consumer_key"].strip()
        self.consumer_secret = keys["twitter_consumer_secret"].strip()
        self.key = keys["twitter_key"].strip()
        self.secret = keys["twitter_secret"].strip()

    def _run(self, data):
        self.api_.update_status(data)
