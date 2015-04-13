#!/usr/bin/env python3
# -*- coding:utf-8 -*-

""" This is main program to test another modules. """

import argparse
import datetime
import xively
from driver import data

__author__ = "Takashi Ando"
__version__ = "0.0.2"
__copyright__ = "Copyright 2015, My own project"
__license__ = "GPL"


def init_args():
    arg = argparse.ArgumentParser(
        description="main program to test TS-MPPT-60 monitor modules")
    arg.add_argument(
        "-n", "--host-name",
        type=str,
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

    return arg.parse_args()


def main(args):
    api = xively.XivelyAPIClient(args.api_key)
    feed = api.feeds.get(args.feed_key)

    now = datetime.datetime.utcnow()
    datastreams = []

    live = data.LiveData(args.host_name)

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


if __name__ == "__main__":
    main(init_args())
