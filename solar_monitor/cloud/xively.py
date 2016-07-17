#!/usr/bin/env python
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

""" Xively Driver class to access xively service. """

import xively
from solar_monitor import logger
from solar_monitor.cloud.base import AbstractCloudServiceDriver


class XivelyServiceDriver(AbstractCloudServiceDriver):
    """ Provide accesor class to Xively cloud service.

    Args:
        api_key: Access key string of write authority.
        feed_key: Feed ID string defined on Xively service.
    Returns:
        Instance object.
    """

    def __init__(self, api_key=None, feed_key=None):
        AbstractCloudServiceDriver(access_key=api_key, service_id=feed_key)

    def _get_client(self, access_key, service_id):
        """ Get the cloud service instance. Child class must implement this
            method to return the cloud service object of the purpose.

        Args:
            access_key: Key string to access the cloud service.
            service_id: ID string to identify the project or something defined on
                the cloud service. (ex. project ID on KeenIo)
        Returns:
            Instance object of cloud service object.
        """
        api = xively.XivelyAPIClient(access_key)
        return api.feeds.get(service_id)

    def get_data_from_server(self):
        pass

    def set_data_to_server(self, rawdata):
        data_source = rawdata["data"]
        at = rawdata["at"]

        logger.debug("send data to keenio at {}".format(at))

        datastreams = []
        for key, data in data_source.items():
            datastreams.append(
                xively.Datastream(
                    id="".join(key.split()),
                    current_value=data["value"],
                    at=at
                )
            )

        self._get_client().datastreams = datastreams
        self._get_client().update()
