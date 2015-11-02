#!/usr/bin/env python3
# -*- coding:utf-8 -*-

""" This module is for... """

import sys
import argparse
import requests
import json
import datetime
import time

DEFAULT_INTERVAL_SEC = 600
DEFAULT_INTERVAL_TYPE = 'discrete'
DEFAULT_DURATION_SEC = 3600
DEFAULT_START_DATE = "2015-10-01T00:00:00Z"
DEFAULT_FEED = '274175384'
URL = "https://api.xively.com/v2/feeds/{}/datastreams"

STREAMS = ('AmpHours',
           'ArrayCurrent',
           'ArrayVoltage',
           'BatteryVoltage',
           'ChargeCurrent',
           'HeatSinkTemperature',
           'KilowattHours',
           'TargetVoltage')
#           'BatteryTemperature',
#           'OutputPower',
#           'SweepPmax',
#           'SweepVoc',


def init_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
            description="script to get data from xively")

    parser.add_argument(
            "-u", "--user",
            type=str,
            default=None,
            help="User acount name of xively account.")

    parser.add_argument(
            "-p", "--password",
            type=str,
            default=None,
            help="User password of xively account.")

    parser.add_argument(
            "-f", "--feed",
            type=str,
            default=DEFAULT_FEED,
            help="Feed ID for xively.")

    parser.add_argument(
            "-i", "--interval",
            type=int,
            default=DEFAULT_INTERVAL_SEC,
            help="Interval sec of stream data getting from xively. " +
                 "Default is " + str(DEFAULT_INTERVAL_SEC) + ".")

    parser.add_argument(
            "-d", "--duration",
            type=int,
            default=3600,
            help="Duration sec of stream data getting from xively. " +
                 "Default is " + str(DEFAULT_DURATION_SEC) + ".")

    parser.add_argument(
            "-s", "--start-date",
            type=str,
            default=DEFAULT_START_DATE,
            help="Start date as UTC getting from xively. " +
                 "Default is " + DEFAULT_START_DATE)

    return parser.parse_args(args)


def get_start_end(start_date_str, duration):
    start = datetime.datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%SZ')
    end = start + datetime.timedelta(0, duration)
    return (start, end)


def get_stream_data(user, password, feed, stream, interval, start, end):
    url = '/'.join((URL.format(feed), stream + '.json?'))
    url = '&'.join((url,
                    'interval=' + str(interval),
                    'interval_type=' + DEFAULT_INTERVAL_TYPE,
                    'start=' + start.isoformat() + 'Z',
                    'end=' + end.isoformat() + 'Z'))
    return requests.get(url, auth=(user, password)).json()


if __name__ == "__main__":
    args = init_args()

    interval = args.interval
    duration = args.duration

    if duration / interval > 1000:
        raise ValueError("Xively has a limit of maximum data number 1000.")

    start, end = get_start_end(args.start_date, duration)
    user = args.user
    password = args.password
    feed = args.feed

    for stream in STREAMS:
        time_out = 10

        while time_out:
            data = get_stream_data(
                    user, password, feed, stream, interval, start, end)

            if "errors" not in data:
                break

            print("{}: {}, {}".format(time_out, data["title"], data["errors"]))

            # must wait for 10 seconds min on xively to get next stream data.
            time.sleep(10)

            time_out -= 1
        else:
            continue

        with open('xively_' + stream + '.json', "w") as fp:
            fp.write(json.dumps(data))
