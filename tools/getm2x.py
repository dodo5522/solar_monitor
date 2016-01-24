#!/usr/bin/env python3
# -*- coding:utf-8 -*-

""" This module is for... """

import sys
import argparse
import requests
import json
import datetime
import time

DEFAULT_DURATION_SEC = 3600
DEFAULT_START_DATE = "2015-10-01T00:00:00Z"
DEFAULT_FEED = '2383efe74fdd4651a867609fe8c9479c'
URL = "http://api-m2x.att.com/v2/devices/{FEED}/streams/{STREAM}/values?"

STREAMS = {
        'ChargeCurrent': {
            'unit': {"symbol": "A", "label": "Amperes"},
            'tag': 'Battery'},
        'TargetVoltage': {
            'unit': {"symbol": "V", "label": "Volts"},
            'tag': 'Battery'},
        'HeatSinkTemperature': {
            'unit': {"symbol": "C", "label": "Celcius"},
            'tag': 'Temperature'},
#        'AmpHours': {
#            'unit': {"symbol": "Ah", "label": "AmpereHours"},
#            'tag': 'Counters'},
#        'ArrayCurrent': {
#            'unit': {"symbol": "A", "label": "Amperes"},
#            'tag': 'Array'},
#        'ArrayVoltage': {
#            'unit': {"symbol": "V", "label": "Volts"},
#            'tag': 'Array'},
#        'BatteryVoltage': {
#            'unit': {"symbol": "V", "label": "Volts"},
#            'tag': 'Battery'},
#        'KilowattHours': {
#            'unit': {"symbol": "kWh", "label": "KilloWattHours"},
#            'tag': 'Counters'},
        }


def init_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
            description="script to get data from m2x")

    parser.add_argument(
            "-u", "--user",
            type=str,
            default=None,
            help="User acount name of m2x account.")

    parser.add_argument(
            "-p", "--password",
            type=str,
            default=None,
            help="User password of m2x account.")

    parser.add_argument(
            "-f", "--feed",
            type=str,
            default=DEFAULT_FEED,
            help="Feed ID for m2x.")

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
            help="Start date as UTC getting from m2x. " +
                 "Default is " + DEFAULT_START_DATE)

    return parser.parse_args(args)


def get_start_end(start_date_str, duration):
    start = datetime.datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%SZ')
    start += datetime.timedelta(0, 0, 0, 0, 0, -9)
    end = start + datetime.timedelta(0, duration)
    return (start, end)


def get_stream_data(user, password, feed, stream, start, end):
    url = URL.format(FEED=feed, STREAM=stream)
    url += '&'.join(('start=' + start.isoformat() + 'Z',
                     'end=' + end.isoformat() + 'Z',
                     'limit=1000'))
    return requests.get(url, auth=(user, password)).json()


if __name__ == "__main__":
    args = init_args()

    start, end = get_start_end(args.start_date, args.duration)
    user = args.user
    password = args.password
    feed = args.feed

    for stream, options in STREAMS.items():
        time_out = 10

        while time_out:
            data = get_stream_data(
                    user, password, feed, stream, start, end)

            if "errors" not in data:
                break

            print("{}: {}: {}, {}".format(
                time_out, stream, data["title"], data["errors"]))

            # must wait for 10 seconds min on m2x to get next stream data.
            time.sleep(10)

            time_out -= 1
        else:
            continue

        new_data = {}
        datapoints = []

        for dat in data["values"]:
            new_now = datetime.datetime.strptime(dat["timestamp"].split(".")[0] + 'Z', '%Y-%m-%dT%H:%M:%SZ')
            new_now += datetime.timedelta(0, 0, 0, 0, 0, 9)
            datapoints.append({"at": new_now.isoformat() + "Z", "value": dat["value"]})

        new_data["datapoints"] = datapoints
        new_data["unit"] = options["unit"]
        new_data["tags"] = [options["tag"], ]
        new_data["id"] = stream

        file_name = "m2x_" + "".join(stream.split(" ")) + "_" + "-".join(args.start_date.split(":")) + '.json'
        with open(file_name, "w") as fp:
            fp.write(json.dumps(new_data))
