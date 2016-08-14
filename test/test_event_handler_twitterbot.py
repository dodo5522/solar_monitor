#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from datetime import datetime
from solar_monitor.event.handler import TweetBotEventHandler
from unittest.mock import patch
from unittest.mock import MagicMock


class TestTweetBotEventHandler(unittest.TestCase):
    """test TweetBotEventHandler class."""

    @classmethod
    def setUpClass(cls):
        sample_data = {}
        sample_data["at"] = datetime(2016, 1, 3, 4, 55, 59)
        sample_data["data"] = {
            "Battery Voltage": {
                "value": 1.0,
                "unit": "V"
            },
            "Array Voltage": {
                "value": 2.0,
                "unit": "V"
            },
            "Array Temparature": {
                "value": 3.0,
                "unit": "C"
            }
        }

        cls.sample_data_ = sample_data

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch("solar_monitor.event.handler.tweepy.OAuthHandler", autospec=True)
    @patch("solar_monitor.event.handler.tweepy.API", autospec=True)
    def test_run_command_default(self, mock_api, mock_oauth_handler):
        # Prepare test environment
        mock_api_obj = MagicMock()
        mock_api_obj.update_status = MagicMock()
        mock_api.return_value = mock_api_obj

        mock_auth_obj = MagicMock()
        mock_auth_obj.set_access_token = MagicMock()
        mock_oauth_handler.return_value = mock_auth_obj

        # Run code to test
        handler = TweetBotEventHandler(
            "dummy_consumer_key",
            "dummy_consumer_secret",
            "dummy_key",
            "dummy_secret")
        handler.start()
        handler.put_q(self.sample_data_)
        handler.join_q()
        handler.stop()
        handler.join()

        # Verify
        mock_oauth_handler.assert_called_once_with(
            consumer_key="dummy_consumer_key",
            consumer_secret="dummy_consumer_secret")

        mock_auth_obj.set_access_token.assert_called_once_with(
            key="dummy_key",
            secret="dummy_secret")

        mock_api.assert_called_once_with(mock_auth_obj)

        mock_api_obj.update_status.assert_called_once_with("バッテリ電圧は1.0Vです。\n2016年1月3日4時55分に取得したデータになります。")

    @patch("solar_monitor.event.handler.tweepy.OAuthHandler", autospec=True)
    @patch("solar_monitor.event.handler.tweepy.API", autospec=True)
    def test_run_command_array_voltage(self, mock_api, mock_oauth_handler):
        # Prepare test environment
        mock_api_obj = MagicMock()
        mock_api_obj.update_status = MagicMock()
        mock_api.return_value = mock_api_obj

        mock_auth_obj = MagicMock()
        mock_auth_obj.set_access_token = MagicMock()
        mock_oauth_handler.return_value = mock_auth_obj

        # Run code to test
        handler = TweetBotEventHandler(
            "dummy_consumer_key",
            "dummy_consumer_secret",
            "dummy_key",
            "dummy_secret",
            msgs=["太陽光パネルの電圧は{VALUE}{UNIT}です。", "{YEAR}年{MONTH}月{DAY}日に取得したデータになります。"],
            value_label="Array Voltage")
        handler.start()
        handler.put_q(self.sample_data_)
        handler.join_q()
        handler.stop()
        handler.join()

        # Verify
        mock_oauth_handler.assert_called_once_with(
            consumer_key="dummy_consumer_key",
            consumer_secret="dummy_consumer_secret")

        mock_auth_obj.set_access_token.assert_called_once_with(
            key="dummy_key",
            secret="dummy_secret")

        mock_api.assert_called_once_with(mock_auth_obj)

        mock_api_obj.update_status.assert_called_once_with("太陽光パネルの電圧は2.0Vです。\n2016年1月3日に取得したデータになります。")

    @patch("solar_monitor.event.handler.tweepy.OAuthHandler", autospec=True)
    @patch("solar_monitor.event.handler.tweepy.API", autospec=True)
    def test_run_command_array_temparature(self, mock_api, mock_oauth_handler):
        # Prepare test environment
        mock_api_obj = MagicMock()
        mock_api_obj.update_status = MagicMock()
        mock_api.return_value = mock_api_obj

        mock_auth_obj = MagicMock()
        mock_auth_obj.set_access_token = MagicMock()
        mock_oauth_handler.return_value = mock_auth_obj

        # Run code to test
        handler = TweetBotEventHandler(
            "dummy_consumer_key",
            "dummy_consumer_secret",
            "dummy_key",
            "dummy_secret",
            msgs=["太陽光パネルの温度は{VALUE}{UNIT}です。", "{YEAR}年{MONTH}月{DAY}日{HOUR}時{MINUTE}分{SECOND}秒に取得したデータになります。"],
            value_label="Array Temparature")
        handler.start()
        handler.put_q(self.sample_data_)
        handler.join_q()
        handler.stop()
        handler.join()

        # Verify
        mock_oauth_handler.assert_called_once_with(
            consumer_key="dummy_consumer_key",
            consumer_secret="dummy_consumer_secret")

        mock_auth_obj.set_access_token.assert_called_once_with(
            key="dummy_key",
            secret="dummy_secret")

        mock_api.assert_called_once_with(mock_auth_obj)

        mock_api_obj.update_status.assert_called_once_with("太陽光パネルの温度は3.0Cです。\n2016年1月3日4時55分59秒に取得したデータになります。")

if __name__ == "__main__":
    unittest.main()
