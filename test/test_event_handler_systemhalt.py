#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import subprocess
import sys
import unittest
from datetime import datetime
from solar_monitor.event.handler import SystemHaltEventHandler
from unittest.mock import patch
from unittest.mock import MagicMock


class TestSystemHaltEventHandler(unittest.TestCase):
    """test KeenIoHandler class."""

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

    @patch("solar_monitor.event.handler.subprocess.Popen", autospec=True)
    def test_run_command(self, mocked_popen):
        cmd_dummy = "shutdown -h now"

        proc = MagicMock()
        proc.communicate = MagicMock(return_value=[b"", b""])
        mocked_popen.return_value = proc

        handler = SystemHaltEventHandler(cmd_dummy)
        handler.start()
        handler.put_q([])
        handler.join_q()
        handler.stop()
        handler.join()

        mocked_popen.assert_called_once_with(cmd_dummy.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @patch("solar_monitor.event.handler.subprocess.Popen", autospec=True)
    def test_not_run_command(self, mocked_popen):
        cmd_dummy = ""

        proc = MagicMock()
        proc.communicate = MagicMock(return_value=[b"", b""])
        mocked_popen.return_value = proc

        handler = SystemHaltEventHandler(cmd_dummy)
        handler.start()
        handler.put_q([])
        handler.join_q()
        handler.stop()
        handler.join()

        if sys.version_info[:2] >= (3, 5):
            mocked_popen.assert_not_called()
        else:
            self.assertFalse(mocked_popen.called)


if __name__ == "__main__":
    unittest.main()
