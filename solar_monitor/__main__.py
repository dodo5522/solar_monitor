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
import argparse
import datetime
import tsmppt60_driver
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


EVENT_TRIGGERS = []
CHARGE_CONTROLLER = tsmppt60_driver


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

    return arg.parse_args()


def start_event_triggers(**kwargs):
    """ Initialize and start event trigger/handler.

    Keyword Args:
        kwargs: see init_args() function to know what option is there.
    Returns:
        None
    """
    data_updated_trigger = DataIsUpdatedTrigger()

    # TODO: default/solar_monitor.confに設定追加したら、kwargsで条件分岐するように修正する
    h = TweetBotEventHandler("/tmp/twitter.conf")
    data_updated_trigger.append(h)

    if kwargs["keenio_project_id"] and kwargs["keenio_write_key"]:
        h = KeenIoEventHandler(
            project_id=kwargs["keenio_project_id"],
            write_key=kwargs["keenio_write_key"])

        data_updated_trigger.append(h)

    if kwargs["xively_api_key"] and kwargs["xively_feed_key"]:
        h = XivelyEventHandler(
            api_key=kwargs["xively_api_key"],
            feed_key=kwargs["xively_feed_key"])
        data_updated_trigger.append(h)

    if kwargs["battery_monitor_enabled"]:
        if kwargs["battery_limit"]:
            bat_low_trigger = BatteryLowTrigger(
                lowest_voltage=kwargs["battery_limit"])

            bat_low_trigger.append(
                SystemHaltEventHandler(
                    cmd=kwargs["battery_limit_hook_script"]))

# FIXME: Implement twittter bot
#    bat_ful_trigger = BatteryFullTrigger(voltage=26.0)
#    panel_tmp_hi_trigger = PanelTempHighTrigger(temp=50.0)
#    panel_tmp_lo_trigger = PanelTempLowTrigger(temp=20.0)

# FIXME: Implement twittter bot
#    if kwargs["twitter_bot_enabled"]:
#        from solar_monitor.event.handler import TweetEventHandler
#
#        h = TweetEventHandler(
#            api_key=kwargs[""],
#            some_id=kwargs[""])
#
#        bat_low_trigger.append(h)
#        bat_ful_trigger.append(h)
#        panel_tmp_hi_trigger.append(h)
#        panel_tmp_lo_trigger.append(h)

    if "data_updated_trigger" in locals():
        EVENT_TRIGGERS.append(data_updated_trigger)
    if "bat_low_trigger" in locals():
        EVENT_TRIGGERS.append(bat_low_trigger)

    for trigger in EVENT_TRIGGERS:
        trigger.start()


def stop_event_triggers():
    """ Stop event trigger/handler. """

    for trigger in EVENT_TRIGGERS:
        trigger.stop()

    for trigger in EVENT_TRIGGERS:
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
    system_status = CHARGE_CONTROLLER.SystemStatus(kwargs["host_name"])

    now = datetime.datetime.utcnow()
    got_data = system_status.get(kwargs["status_all"])

    rawdata = {}
    rawdata["source"] = "solar"
    rawdata["data"] = got_data
    rawdata["at"] = now

    for key, data in got_data.items():
        logger.info(
            "{date}: {group}, {elem}, {value}[{unit}]".format(
                date=now, group=data["group"], elem=key,
                value=str(data["value"]), unit=data["unit"]))

    for trigger in EVENT_TRIGGERS:
        trigger.put_q(rawdata)

    for trigger in EVENT_TRIGGERS:
        trigger.join_q()


def main():
    args = init_args()
    kwargs = dict(args._get_kwargs())

    logger.configure(path_file=args.log_file, is_debug=args.debug)

    if args.just_get_status:
        event_loop(**kwargs)
        return

    start_event_triggers(**kwargs)

    kwargs = {}
    kwargs["host_name"] = args.host_name
    kwargs["status_all"] = args.status_all
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
        stop_event_triggers()

main()
