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

import logging

LOGGER = logging.getLogger("solar_monitor")


def configure(
        path_file="/var/log/solar_monitor.log",
        log_format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        date_format="%Y/%m/%d %p %l:%M:%S",
        is_debug=False):
    """ Configure the logger module to store log onto some file or stdout.

    Args:
        path_file: File path string to store log.
        log_format: String to specify the format to logging module.
        date_format: String to specify the format of date to logging module.
        debug: Set debug level as logging.DEBUG if True.
    Returns:
        None
    """
    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)

    if path_file:
        handler = logging.FileHandler(path_file, mode="a")
        handler.setFormatter(formatter)
        LOGGER.addHandler(handler)

    # to print message with all level if debug is True.
    LOGGER.setLevel(logging.NOTSET if is_debug else logging.WARNING)


def debug(message):
    """ Print message for debug to stdout, log file, or both according to
        the initialized setting.

    Args:
        message: String of message to print.
    """
    LOGGER.debug(message)


def info(message):
    """ Print message for debug to stdout, log file, or both according to
        the initialized setting.

    Args:
        message: String of message to print.
    """
    LOGGER.debug(message)


def warning(message):
    """ Print message for debug to stdout, log file, or both according to
        the initialized setting.

    Args:
        message: String of message to print.
    """
    LOGGER.debug(message)


def error(message):
    """ Print message for debug to stdout, log file, or both according to
        the initialized setting.

    Args:
        message: String of message to print.
    """
    LOGGER.debug(message)


def critical(message):
    """ Print message for debug to stdout, log file, or both according to
        the initialized setting.

    Args:
        message: String of message to print.
    """
    LOGGER.debug(message)
