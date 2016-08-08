#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import unittest
from datetime import datetime
from solar_monitor.event.handler import TweetBotEventHandler
from unittest.mock import patch
from unittest.mock import MagicMock


class TestTweetBotEventHandler(unittest.TestCase):
    """test TweetBotEventHandler class."""

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_run_command(self):
        handler = TweetBotEventHandler("/Users/takashi/Development/solar_monitor/twitter.conf")
        handler.start()
        handler.put_q("bot test at " + str(datetime.now()) + ".")
        handler.join_q()
        handler.stop()
        handler.join()

        # mocked_popen.assert_called_once_with(cmd_dummy.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


if __name__ == "__main__":
    unittest.main()
