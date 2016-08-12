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
from solar_monitor import logger
from solar_monitor.timer import RecursiveTimer
from solar_monitor.event.trigger import DataIsUpdatedTrigger
from solar_monitor.event.trigger import BatteryLowTrigger
# from solar_monitor.event.trigger import BatteryFullTrigger
# from solar_monitor.event.trigger import PanelTempHighTrigger
# from solar_monitor.event.trigger import PanelTempLowTrigger
from solar_monitor.event.handler import SystemHaltEventHandler
from solar_monitor.event.handler import KeenIoEventHandler
from solar_monitor.event.handler import XivelyEventHandler
from solar_monitor.event.handler import TweetBotEventHandler


def init_triggers(**kwargs):
    """ Initialize event triggers and handlers according to settings.

    Keyword Args:
        kwargs: see init_args() function to know what option is there.
    Returns:
        list of event triggers which have event hnadlers according to config setting.
    """
    data_updated_trigger = DataIsUpdatedTrigger()

    def get_configs(*configs):
        for conf in configs:
            if not conf:
                return ()
        return configs

    configs = get_configs(
        kwargs["keenio_project_id"], kwargs["keenio_write_key"])

    if configs:
        data_updated_trigger.append(KeenIoEventHandler(*configs))

    configs = get_configs(
        kwargs["xively_api_key"], kwargs["xively_feed_key"])

    if configs:
        data_updated_trigger.append(XivelyEventHandler(*configs))

    configs = get_configs(
        kwargs["battery_monitor_enabled"],
        kwargs["battery_limit"],
        kwargs["battery_limit_hook_script"])

    if configs:
        bat_low_trigger = BatteryLowTrigger(configs[1])

        bat_low_trigger.append(
            SystemHaltEventHandler(configs[2]))

    configs = get_configs(
        kwargs["twitter_consumer_key"],
        kwargs["twitter_consumer_secret"],
        kwargs["twitter_key"],
        kwargs["twitter_secret"])

    if configs:
        data_updated_trigger.append(TweetBotEventHandler(*configs))

#    bat_ful_trigger = BatteryFullTrigger(voltage=26.0)
#    panel_tmp_hi_trigger = PanelTempHighTrigger(temp=50.0)
#    panel_tmp_lo_trigger = PanelTempLowTrigger(temp=20.0)

    triggers = []

    if "data_updated_trigger" in locals():
        triggers.append(data_updated_trigger)
    if "bat_low_trigger" in locals():
        triggers.append(bat_low_trigger)

    return triggers


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
    host_name = kwargs["host_name"]
    is_status_all = kwargs["status_all"]
    triggers = kwargs["triggers"]

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

    for trigger in triggers:
        trigger.put_q(rawdata)

    for trigger in triggers:
        trigger.join_q()


def main():
    args = argparser.init()
    kwargs = dict(args._get_kwargs())

    logger.configure(path_file=args.log_file, is_debug=args.debug)

    if args.just_get_status:
        event_loop(**kwargs)
        return

    triggers = init_triggers(**kwargs)
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
    except:
        e = sys.exc_info()
        logger.debug("Another exception: " + str(e[0]) + " is raised.")
        raise
    finally:
        timer.cancel()
        stop_triggers(triggers)

main()
