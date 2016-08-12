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

    @patch("solar_monitor.event.handler.tweepy.OAuthHandler", autospec=True)
    @patch("solar_monitor.event.handler.tweepy.API", autospec=True)
    def test_run_command(self, mock_api, mock_oauth_handler):
        mock_auth_obj = MagicMock()
        mock_auth_obj.set_access_token = MagicMock()
        mock_oauth_handler.return_value = mock_auth_obj

        data = {}
        data["at"] = datetime(2016, 1, 3, 4, 55, 59)
        data["data"] = {
            "Battery Voltage": {
                "value": 1.0
            }
        }

        handler = TweetBotEventHandler(
            "dummy_consumer_key",
            "dummy_consumer_secret",
            "dummy_key",
            "dummy_secret")
        handler.start()
        handler.put_q(data)
        handler.join_q()
        handler.stop()
        handler.join()

        mock_oauth_handler.assert_called_once_with(
            consumer_key="dummy_consumer_key",
            consumer_secret="dummy_consumer_secret")

        mock_auth_obj.set_access_token.assert_called_once_with(
            key="dummy_key",
            secret="dummy_secret")

if __name__ == "__main__":
    unittest.main()
