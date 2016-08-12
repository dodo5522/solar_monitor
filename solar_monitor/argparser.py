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

import sys
import argparse


def init(argv=sys.argv[1:]):
    """ Return the parsed arguments specified to sys.argv.

    Args:
        argv: sys.argv[1:] as default.
    Returns:
        Dict like object.
    """
    arg = argparse.ArgumentParser(
        description="main program to test TS-MPPT-60 monitor modules")
    arg.add_argument(
        "-n", "--host-name",
        type=str,
        default="192.168.1.20",
        help="TS-MPPT-60 host address"
    )
    arg.add_argument(
        "-xa", "--xively-api-key",
        type=str,
        nargs='?', default=None, const=None,
        help="Xively API key string"
    )
    arg.add_argument(
        "-xf", "--xively-feed-key",
        type=int,
        nargs='?', default=None, const=None,
        help="Xively feed key"
    )
    arg.add_argument(
        "-kp", "--keenio-project-id",
        type=str,
        nargs='?', default=None, const=None,
        help="keenio project id string"
    )
    arg.add_argument(
        "-kw", "--keenio-write-key",
        type=str,
        nargs='?', default=None, const=None,
        help="keenio write key"
    )
    arg.add_argument(
        "-tck", "--twitter-consumer-key",
        type=str,
        nargs='?', default=None, const=None,
        help="Consumer Key (API Key)"
    )
    arg.add_argument(
        "-tcs", "--twitter-consumer-secret",
        type=str,
        nargs='?', default=None, const=None,
        help="Consumer Secret (API Secret)"
    )
    arg.add_argument(
        "-tk", "--twitter-key",
        type=str,
        nargs='?', default=None, const=None,
        help="Access Token"
    )
    arg.add_argument(
        "-ts", "--twitter-secret",
        type=str,
        nargs='?', default=None, const=None,
        help="Access Token Secret"
    )
    arg.add_argument(
        "-be", "--battery-monitor-enabled",
        action="store_true",
        default=False,
        help="enable battery monitor"
    )
    arg.add_argument(
        "-bl", "--battery-limit",
        type=float,
        nargs='?', default=11.5, const=11.5,
        help="battery voltage limit like 11.5"
    )
    arg.add_argument(
        "-bs", "--battery-limit-hook-script",
        type=str, nargs='?',
        default="/usr/local/bin/remote_shutdown.sh",
        const="/usr/local/bin/remote_shutdown.sh",
        help="path to hook sript run at limit of battery"
    )
    arg.add_argument(
        "-i", "--interval",
        type=int,
        default=300,
        help="Xively update interval with sec"
    )
    arg.add_argument(
        "-l", "--log-file",
        type=str,
        default=None,
        help="log file path to output"
    )
    arg.add_argument(
        "--just-get-status",
        action='store_true',
        default=False,
        help="Just get status of charge controller"
    )
    arg.add_argument(
        "--status-all",
        action='store_false',
        default=True,
        help="Get all status of charge controller"
    )
    arg.add_argument(
        "--debug",
        action='store_true',
        default=False,
        help="Enable debug mode"
    )

    return arg.parse_args(argv)
