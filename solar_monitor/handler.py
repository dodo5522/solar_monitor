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
from solar_monitor import logger
from event_listener.base import IEventHandler


class SystemHaltEventHandler(IEventHandler):
    """ The instance should be registered to event trigger of low battery. Run
        command specified to "cmd" like "./set_event.sh shutdown" when the event
        triggered.

    Args:
        cmd: command to be run when the event is triggered.
        q_max: internal queue size to be used from another thread.
    Returns:
        Instance of this class.
    """

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
