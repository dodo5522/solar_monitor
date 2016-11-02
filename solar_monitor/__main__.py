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
import time
import datetime
import tsmppt60_driver as CHARGE_CONTROLLER
from solar_monitor import argparser
from solar_monitor import config
from solar_monitor import logger
from solar_monitor.timer import RecursiveTimer


def start_triggers(triggers):
    """ Start all event triggers. At the same time, the all event handler
        included in the event triggers also starts.

    Args:
        triggers: List of event trigger to be started.
    Returns:
        None
    """
    for trigger in triggers:
        trigger.start()


def stop_triggers(triggers):
    """ Stop event trigger/handler.

    Args:
        triggers: List of event trigger to be started.
    Returns:
        None
    """
    for trigger in triggers:
        trigger.stop()

    for trigger in triggers:
        trigger.join()


def put_to_triggers(triggers, data):
    """ Put data to all event trigger.

    Args:
        triggers: List of event trigger to be started.
        data: data object to be put to all trigger.
    Returns:
        None
    """
    for trigger in triggers:
        trigger.put_q(data)

    for trigger in triggers:
        trigger.join_q()


def event_loop(**kwargs):
    """ Monitor charge controller and update database like xively or
        internal database. This method should be called with a timer.

    Args:
        kwargs: keyword argument object
    Returns:
        None
    Exceptions:
        queue.Full: If queue of event handler is full
    """
    host_name = kwargs.get("host_name")
    is_status_all = kwargs.get("status_all")
    triggers = kwargs.get("triggers")

    if None in (host_name, is_status_all, triggers):
        return

    now = datetime.datetime.utcnow()
    system_status = CHARGE_CONTROLLER.SystemStatus(host_name)
    got_data = system_status.get(is_status_all)

    rawdata = {}
    rawdata["source"] = "solar"
    rawdata["data"] = got_data
    rawdata["at"] = now

    for key, data in got_data.items():
        logger.info(
            "{date}: {group}, {elem}, {value}[{unit}]".format(
                date=now, group=data["group"], elem=key,
                value=str(data["value"]), unit=data["unit"]))

    put_to_triggers(triggers, rawdata)


def main():
    args = argparser.init()
    kwargs = dict(args._get_kwargs())

    logger.configure(path_file=args.log_file, is_debug=args.debug)

    if args.just_get_status:
        event_loop(**kwargs)
        return

    triggers = config.init_triggers(**kwargs)
    start_triggers(triggers)

    kwargs = {}
    kwargs["host_name"] = args.host_name
    kwargs["status_all"] = args.status_all
    kwargs["triggers"] = triggers
    timer = RecursiveTimer(args.interval, event_loop, **kwargs)

    try:
        timer.start()
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logger.debug("monitor program will be killed by user.")
        raise
    except:
        e = sys.exc_info()
        logger.debug("Another exception: " + str(e[0]) + " is raised.")
        raise
    finally:
        timer.cancel()
        stop_triggers(triggers)

main()
