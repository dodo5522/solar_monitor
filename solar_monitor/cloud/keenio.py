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

from keen.client import KeenClient
from solar_monitor import logger
from solar_monitor.cloud.base import ICloudService


class KeenIoCloudService(ICloudService):
    """ Provide accesor class to KeenIo cloud service.

    Args:
        project_id: Project ID string defined on KeenIo service.
        write_key: Access key string of write authority.
    Returns:
        Instance object.
    """

    def __init__(self, project_id=None, write_key=None):
        self.client_ = KeenClient(
            project_id=project_id,
            write_key=write_key)

    def get_data_from_server(self):
        return None

    def set_data_to_server(self, rawdata):
        data_source = rawdata["source"]
        at = rawdata["at"]

        datalist_keenio = []
        for monitoring_item, at in rawdata["data"].items():
            data_for_keenio = at
            data_for_keenio["label"] = monitoring_item
            data_for_keenio["source"] = data_source
            data_for_keenio["keen"] = {"timestamp": at.isoformat() + "Z"}
            datalist_keenio.append(data_for_keenio)

        self.client_.add_events({"offgrid": datalist_keenio})

        logger.debug("{} sent data to keenio at {}".format(
            type(self).__name__, at))
