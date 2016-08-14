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
    """ Tweet bot handler. Tweets some messages on your twitter account.

    Args:
        consumer_key: Consumer Key (API Key)
        consumer_secret: Consumer Secret (API Secret)
        key: Access Token
        secret: Access Token Secret
        msgs: list of messages
        value_label: data's label you want to show on msgs as VALUE label
        q_max: Queue size of internal.

    Returns:
        IEventHandler object.
    """
    def __init__(
            self,
            consumer_key,
            consumer_secret,
            key,
            secret,
            msgs=["バッテリ電圧は{VALUE}{UNIT}です。", "{YEAR}年{MONTH}月{DAY}日{HOUR}時{MINUTE}分に取得したデータになります。"],
            value_label="Battery Voltage",
            q_max=5):

        IEventHandler.__init__(self, q_max=q_max)

        auth = tweepy.OAuthHandler(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret)
        auth.set_access_token(key=key, secret=secret)

        self.api_ = tweepy.API(auth)
        self.msg_ = "\n".join(msgs)
        self.label_ = value_label

    def _run(self, data):
        at = data["at"]

        msg = self.msg_.format(
            YEAR=at.year, MONTH=at.month, DAY=at.day, HOUR=at.hour, MINUTE=at.minute, SECOND=at.second,
            UNIT=data["data"][self.label_]["unit"],
            VALUE=round(number=data["data"][self.label_]["value"], ndigits=2))

        self.api_.update_status(msg)
