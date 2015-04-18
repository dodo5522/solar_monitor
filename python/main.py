#!/usr/bin/env python3
# -*- coding:utf-8 -*-

""" This is main program to test another modules. """

import time
import threading
import argparse
import datetime
import xively
import driver.livedata

__author__ = "Takashi Ando"
__version__ = "0.0.2"
__copyright__ = "Copyright 2015, My own project"
__license__ = "GPL"


class RecursiveTimer(object):
    """ Class of timer for recursively running function. """
    def __init__(self, func, intarval_sec=300, is_resursive=True):
        self._func = func
        self._interval = intarval_sec
        self._is_recursive = is_resursive
        self._thread = threading.Timer(self._interval, self._tick)

    def _tick(self):
        if self._is_recursive:
            self._thread = threading.Timer(self._interval, self._tick)
            self._thread.start()

        self._func()

    def start(self):
        self._thread.start()

    def cancel(self):
        self._thread.cancel()


def init_args():
    arg = argparse.ArgumentParser(
        description="main program to test TS-MPPT-60 monitor modules")
    arg.add_argument(
        "-n", "--host-name",
        type=str,
        default="192.168.1.20",
        help="TS-MPPT-60 host address"
    )
    arg.add_argument(
        "-a", "--api-key",
        type=str,
        help="Xively API key string"
    )
    arg.add_argument(
        "-f", "--feed-key",
        type=int,
        help="Xively feed key"
    )
    arg.add_argument(
        "-i", "--interval",
        type=int,
        default=300,
        help="Xively update interval with sec"
    )

    return arg.parse_args()


def main(args):
    api = xively.XivelyAPIClient(args.api_key)
    feed = api.feeds.get(args.feed_key)

    def update():
        print("update called")
        now = datetime.datetime.utcnow()
        datastreams = []

        live = driver.livedata.LiveData(args.host_name)

        for group in live._data_objects:
            for data_in_group in live._data_objects[group].get_all():
                print(group + " : " + ", ".join(data_in_group))
                datastreams.append(
                    xively.Datastream(
                        id="".join(data_in_group[0].split()),
                        current_value=float(data_in_group[1]),
                        at=now
                    )
                )

        feed.datastreams = datastreams
        feed.update()

    timer = RecursiveTimer(update, args.interval)

    try:
        timer.start()
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        timer.cancel()


if __name__ == "__main__":
    main(init_args())
