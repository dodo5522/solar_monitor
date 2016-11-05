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
    Exceptions:
        queue.Full: If queue of event handler is full
    """
    for trigger in triggers:
        trigger.put_q(data)

    for trigger in triggers:
        trigger.join_q()


def get_controller_status(host, is_all=True, is_debug=False):
    """ Get the charge controller status.

    Args:
        host: host name or address like 192.168.1.20
        is_all: get all status data if True
        is_debug: dump the got data if True
    Returns:
        Got data from charge controller
    Exceptions:
        requests.exceptions.ConnectTimeout
        requests.exceptions.ConnectionError
        requests.exceptions.HTTPError
        requests.exceptions.ReadTimeout
        requests.exceptions.RequestException
        requests.exceptions.RetryError
        requests.exceptions.SSLError
        requests.exceptions.Timeout
        requests.exceptions.TooManyRedirects
    """
    system_status = CHARGE_CONTROLLER.SystemStatus(host)
    got_data = system_status.get(is_all)

    if is_debug:
        for key, data in got_data.items():
            logger.info(
                "{group}, {elem}, {value}[{unit}]".format(
                    group=data["group"], elem=key,
                    value=str(data["value"]), unit=data["unit"]))

    return got_data


def timer_handler(host, triggers=[], is_all=True, is_debug=False):
    """ Monitor charge controller and update database like xively or
        internal database. This method should be called with a timer.

    Args:
        host: host name or address like 192.168.1.20
        triggers: event trigger class objects
        is_all: get all status data if True
        is_debug: dump the got data if True
    Returns:
        None
    Exceptions:
        queue.Full: If queue of event handler is full
    """
    rawdata = {}
    rawdata["source"] = "solar"
    rawdata["at"] = datetime.datetime.utcnow()
    rawdata["data"] = get_controller_status(host, is_all, is_debug)

    put_to_triggers(triggers, rawdata)


def main():
    args = argparser.init()
    kwargs = dict(args._get_kwargs())

    logger.configure(path_file=args.log_file, is_debug=args.debug)

    if args.just_get_status:
        try:
            get_controller_status(
                host=args.host_name, is_all=args.status_all, is_debug=True)
        except Exception as e:
            logger.error("Exception raised at just getting status: " + type(e).__name__)
            logger.error("Detail: " + str(e))
        finally:
            return

    triggers = config.init_triggers(**kwargs)
    start_triggers(triggers)

    timer = RecursiveTimer(
        args.interval, timer_handler,
        host=args.host_name, is_all=args.status_all, triggers=triggers, is_debug=args.debug)
    timer.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logger.debug("monitor program will be killed by user.")
        raise
    except:
        e = sys.exc_info()
        logger.debug("Another exception raised: " + type(e[0]).__name__)
        logger.debug("Detail: " + str(e[0]))
        raise
    finally:
        timer.cancel()
        stop_triggers(triggers)

main()
