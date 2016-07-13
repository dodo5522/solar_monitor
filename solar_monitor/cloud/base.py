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

"""
Cloud service driver class definition. The inheritance tree structure is like
below. These event handler class objects work with threading by the data or
configuration set when initialized.

AbstractCloudServiceDriver
    |- KeenIoCloudServiceDriver : for KeenIO
    `- XivelyCloudServiceDriver : for Xively
"""


class AbstractCloudServiceDriver(object):
    """ Abstract class of cloud service.

    Args:
        access_key: Key string to access the cloud service.
        service_id: ID string to identify the project or something defined on
            the cloud service. (ex. project ID on KeenIo)
    Returns:
        Instance object of cloud service driver.
    """

    def __init__(self, access_key=None, service_id=None):
        self.service_ = self._get_service(access_key, service_id)

    def _get_service(self, access_key, service_id):
        """ Get the cloud service instance. Child class must implement this
            method to return the cloud service object of the purpose.

        Args:
            access_key: Key string to access the cloud service.
            service_id: ID string to identify the project or something defined on
                the cloud service. (ex. project ID on KeenIo)
        Returns:
            Instance object of cloud service object.
        """
        raise NotImplementedError

    def get_data_from_server(self):
        raise NotImplementedError

    def set_data_to_server(self, rawdata):
        raise NotImplementedError
