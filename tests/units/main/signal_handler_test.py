# Signal handler test classes.
#
# This file is part of Simpleline Text UI library.
#
# Copyright (C) 2020  Red Hat, Inc.
#
# Simpleline is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Simpleline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Simpleline.  If not, see <https://www.gnu.org/licenses/>.
#


import unittest

from unittest.mock import patch, MagicMock

from simpleline import App
from simpleline.event_loop.signals import RenderScreenSignal, AbstractSignal
from simpleline.render.screen import UIScreen


class SignalHandler_TestCase(unittest.TestCase):

    def setUp(self):
        self.callback_called = False
        self.priority = 0

    def _callback(self, signal, data):
        self.callback_called = True
        signal.test_attribute = True

    def test_basic_connect(self):
        connect_screen = UIScreen()

        App.initialize(scheduler=MagicMock())
        connect_screen.connect(TestSignal, self._callback)
        App.get_event_loop().enqueue_signal(TestSignal(self))
        App.get_event_loop().process_signals()

        self.assertTrue(self.callback_called)

    def test_create_signal(self):
        connect_screen = UIScreen()

        App.initialize(scheduler=MagicMock())
        signal = connect_screen.create_signal(TestSignal, priority=20)

        self.assertEqual(signal.priority, 20)
        self.assertTrue(isinstance(signal, TestSignal))
        # source is set by create_signal
        self.assertEqual(signal.source, connect_screen)

    def test_emit(self):
        connect_screen = UIScreen()

        App.initialize(scheduler=MagicMock())
        connect_screen.connect(TestSignal, self._callback)
        connect_screen.emit(TestSignal(self))
        App.get_event_loop().process_signals()

        self.assertTrue(self.callback_called)

    @patch('sys.stdout')
    def test_connect_react_on_rendering(self, _):
        connect_test_screen = TestRenderConnectHandler()
        screen2 = EmptyScreen()

        App.initialize()
        App.get_scheduler().schedule_screen(connect_test_screen)
        App.get_scheduler().schedule_screen(screen2)
        App.run()

        self.assertTrue(connect_test_screen.callback_called)


class TestRenderConnectHandler(UIScreen):

    def __init__(self):
        super().__init__()
        self.callback_called = False
        self.input_required = False

    def refresh(self, args=None):
        super().refresh(args)
        self.connect(RenderScreenSignal, self._callback)
        self.close()

    def _callback(self, signal, args):
        self.callback_called = True


class EmptyScreen(UIScreen):

    def __init__(self):
        super().__init__()
        self.input_required = False

    def show_all(self):
        super().show_all()
        self.close()


class TestSignal(AbstractSignal):
    pass
